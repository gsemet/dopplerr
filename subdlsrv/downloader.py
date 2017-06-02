# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import glob
import logging
import os


class Downloader(object):
    def __init__(self, args):
        self.args = args

    def process_notify_request(self, request):
        logging.debug("Processing request: %r", request)
        res = {
            'status': "unprocessed"
        }
        if "Series" in request:
            if request.get("EventType") == "Download":
                return self.process_sonarr_on_download_request(request, res)
            return self.failed(res, "Unsupported Sonarr request type: %r", request.get("EventType"))
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
        if self.args.basedir:
            logging.debug("Reconstructing full media path with basedir '%s'",
                          self.args.basedir)
            root_dir = os.path.join(self.args.basedir, root_dir)
        basename = request.get("Series", {}).get("Path")
        logging.info("Searching episodes for serie '%s' in '%s'", serie_title, root_dir)
        self.update_status(res, "searching")
        for episode in request.get("Episodes", []):
            basename = episode.get("SceneName", "")
            episode_title = episode.get("Title", "")
            logging.debug("Searching episode '%s' with base filename '%s'",
                          episode_title, basename)
            found = self.searchFile(root_dir, basename)
            logging.debug("All found files: %r", found)
        return res

    def failed(self, res, message):
        logging.error(message)
        res["status"] = "failed"
        res["error_msg"] = message.lower()
        return res

    def update_status(self, res, status):
        res["status"] = status

    def searchFile(self, root_dir, base_name):
        # This won't work under python 2
        found = []
        for filename in glob.iglob(os.path.join(root_dir,
                                                "**",
                                                "*" + base_name + "*"), recursive=True):
            logging.debug("Found: %s", filename)
            found.append(filename)
        return found
