# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

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
        if not root_dir:
            return self.failed(res, "Empty Series Path")
        if self.args.basedir:
            logging.debug("Reconstructing full media path with basedir '%s'",
                          self.args.basedir)
            root_dir = os.path.join(self.args.basedir, root_dir)
        logging.info("Searching media in '%s'", root_dir)
        self.update_status(res, "searching")
        return res

    def failed(self, res, message):
        logging.error(message)
        res["status"] = "failed"
        res["error_msg"] = message.lower()
        return res

    def update_status(self, res, status):
        res["status"] = status
