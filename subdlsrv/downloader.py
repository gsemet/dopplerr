# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import glob
import logging
import os
import threading

from babelfish import Language
from subliminal import Video
from subliminal import download_best_subtitles
from subliminal import region
from subliminal import save_subtitles
# from subliminal import scan_videos
from subliminal.subtitle import get_subtitle_path

from subdlsrv.txutils import deferredAsThread
from subdlsrv.utils import recursive_iglob


class Downloader(object):
    def __init__(self, args):
        self.args = args
        # Avoid having 2 download at the same time, at least of the integrity of the cache file
        self.subliminal_download_lock = threading.Lock()

    @staticmethod
    def initialize_subliminal():
        logging.info("Initializing Subliminal cache...")
        region.configure('dogpile.cache.dbm', arguments={'filename': 'cachefile.dbm'})

    @deferredAsThread
    def process_notify_request(self, request):
        logging.debug("Processing request: %r", request)
        res = {'status': "unprocessed"}
        if "Series" in request:
            if request.get("EventType") == "Download":
                return self.process_sonarr_on_download_request(request, res)
            return self.failed(
                res, "Unsupported Sonarr request type: {!r}".format(request.get("EventType")))
        return self.failed(res, "Unable to find request type. Does not appear to be Sonarr's")

    def process_sonarr_on_download_request(self, request, res):
        logging.debug("Processing Sonarr's 'on downloaded' event")
        self.update_status(res, "processing")
        res["request_type"] = "sonarr"
        res["request_event"] = "on download"
        root_dir = request.get("Series", {}).get("Path")
        serie_title = request.get("Series", {}).get("Title")
        if not root_dir:
            return self.failed(res, "Empty Series Path")
        root_dir = self.appy_path_mapping(root_dir)
        logging.debug("Root folder: %s", root_dir)
        if self.args.basedir:
            logging.debug("Reconstructing full media path with basedir '%s'", self.args.basedir)

            def concat_path(a, b):
                if not a.endswith('/'):
                    a += '/'
                if b.startswith('/'):
                    b = b[1:]
                a += b
                return a

            root_dir = concat_path(self.args.basedir, root_dir)
        basename = request.get("Series", {}).get("Path")
        logging.info("Searching episodes for serie '%s' in '%s'", serie_title, root_dir)
        self.update_status(res, "searching")
        for episode in request.get("Episodes", []):
            basename = episode.get("SceneName", "")
            episode_title = episode.get("Title", "")
            logging.debug("Searching episode '%s' with base filename '%s'", episode_title, basename)
            if not os.path.exists(root_dir):
                return self.failed(res, "Path does not exists: {}".format(root_dir))
            found = self.search_file(root_dir, basename)
            logging.debug("All found files: %r", found)
        if not found:
            self.update_status(res, "finished", "no file found")
        else:
            return self.download_missing_subtitles(res, found)
        return res

    def failed(self, res, message):
        logging.error(message)
        res["status"] = "failed"
        res["message"] = message.lower()
        return res

    def update_status(self, res, status, message=None):
        res["status"] = status
        if message is not None:
            res["message"] = message
        elif "message" in res:
            del res["message"]

    def search_file(self, root_dir, base_name):
        # This won't work with python < 3.5
        found = []
        protected_path = os.path.join(root_dir, "**", "*" + base_name + "*")
        protected_path = protected_path.replace("[", "[[]").replace("]", "[]]")
        for filename in recursive_iglob(protected_path):
            logging.debug("Found: %s", filename)
            found.append(filename)
        return found

    @deferredAsThread
    def process_fullscan(self, _request):
        logging.debug("Processing full scan of missing subtitle files...")
        res = {
            'status': 'unprocessed',
            'message': 'not implemented yet!',
        }
        return res

    def appy_path_mapping(self, root_dir):
        if not self.args.path_mapping:
            return root_dir
        if root_dir.startswith("/"):
            absolute = True
            root_dir = root_dir[1:]
        for mapping in self.args.path_mapping:
            logging.debug("Mapping: %s", mapping)
            k, _, v = mapping.partition("=")
            logging.debug("Applying mapping %s => %s", k, v)
            if root_dir.startswith(k):
                root_dir = v + root_dir[len(k):]
                break
        if absolute:
            return "/" + root_dir
        return root_dir

    def download_missing_subtitles(self, res, files):
        logging.info("Searching and downloading missing subtitles")
        self.update_status(res, "downloading", "downloading missing subtitles")
        videos = []
        for f in files:
            _, ext = os.path.splitext(f)
            if ext in [".jpeg", ".jpg", ".nfo", ".srt", ".sub", ".nbz"]:
                logging.debug("Ignoring %s because of extension: %s", f, ext)
                continue
            videos.append(Video.fromname(f))
        logging.info("Video files: %r", videos)
        if not videos:
            logging.debug("No subtitle to download")
            self.update_status(res, "finished", "no video file found")
            return res
        self.update_status(res, "fetching", "finding best subtitles")
        self.subliminal_download_lock.acquire()
        subtitles = download_best_subtitles(videos, {Language('eng'), Language('fra')})
        self.subliminal_download_lock.release()
        subtitles_info = []
        for v in videos:
            logging.info("Found subtitles for %s:", v)
            for s in subtitles[v]:
                logging.info("  %s from %s", s.language, s.provider_name)
                subtitles_info.append({
                    "language": str(s.language),
                    "provider": s.provider_name,
                    "filename": get_subtitle_path(v.name, language=s.language)
                })
            save_subtitles(v, subtitles[v])
        self.update_status(res, "finished", "download successful")
        res["subtitles"] = subtitles_info
        return res
