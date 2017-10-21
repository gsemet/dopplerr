# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os
import threading

# from subliminal import scan_videos
from babelfish import Language
from subliminal import Video
from subliminal import download_best_subtitles
from subliminal import region
from subliminal import save_subtitles
from subliminal.subtitle import get_subtitle_path
from txwebbackendbase.singleton import singleton
from txwebbackendbase.threading import deferredAsThread
from txwebbackendbase.utils import recursive_iglob

from dopplerr.request_filter import NotificationFilters
from dopplerr.response import Response
from dopplerr.status import DopplerrStatus

log = logging.getLogger(__name__)


@singleton
class Downloader(object):
    def __init__(self):
        # Avoid having 2 download at the same time, at least of the integrity of the cache file
        self.subliminal_download_lock = threading.Lock()

    @staticmethod
    def initialize_subliminal():
        log.info("Initializing Subliminal cache...")
        region.configure('dogpile.cache.dbm', arguments={'filename': 'cachefile.dbm'})

    @deferredAsThread
    def process_notify_request(self, request):
        log.debug("Processing request: %r", request)
        res = Response({'status': "unprocessed"})
        NotificationFilters().filter(request, res)
        candidates = res.get("candidates")
        if not candidates:
            log.debug("No candidate found")
            res.update_status("finished", "no candidates found")
            return res
        for candidate in candidates:
            found = self.search_file(candidate['root_dir'], candidate['basename'])
            log.debug("All found files: %r", found)
        if not found:
            res.update_status("finished", "candidates found but no video file found")
        else:
            return self.download_missing_subtitles(res, found)

    def search_file(self, root_dir, base_name):
        # This won't work with python < 3.5
        found = []
        protected_path = os.path.join(root_dir, "**", "*" + base_name + "*")
        protected_path = protected_path.replace("[", "[[]").replace("]", "[]]")
        for filename in recursive_iglob(protected_path):
            log.debug("Found: %s", filename)
            found.append(filename)
        return found

    @deferredAsThread
    def process_fullscan(self, _request):
        log.debug("Processing full scan of missing subtitle files...")
        res = {
            'status': 'unprocessed',
            'message': 'not implemented yet!',
        }
        return res

    def download_missing_subtitles(self, res, files):
        log.info("Searching and downloading missing subtitles")
        res.update_status("downloading", "downloading missing subtitles")
        videos = []
        for fil in files:
            _, ext = os.path.splitext(fil)
            if ext in [".jpeg", ".jpg", ".nfo", ".srt", ".sub", ".nbz"]:
                log.debug("Ignoring %s because of extension: %s", fil, ext)
                continue
            videos.append(Video.fromname(fil))
        log.info("Video files: %r", videos)
        if not videos:
            log.debug("No subtitle to download")
            res.update_status("finished", "no video file found")
            return res
        res.update_status("fetching", "finding best subtitles")
        self.subliminal_download_lock.acquire()
        subtitles = download_best_subtitles(videos, {Language(l) for l in DopplerrStatus.languages})
        self.subliminal_download_lock.release()
        subtitles_info = []
        for vid in videos:
            log.info("Found subtitles for %s:", vid)
            for sub in subtitles[vid]:
                log.info("  %s from %s", sub.language, sub.provider_name)
                subtitles_info.append({
                    "language": str(sub.language),
                    "provider": sub.provider_name,
                    "filename": get_subtitle_path(vid.name, language=sub.language)
                })
            save_subtitles(vid, subtitles[vid])
        res.update_status("finished", "download successful")
        res["subtitles"] = subtitles_info
        return res
