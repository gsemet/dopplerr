# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

log = logging.getLogger(__name__)


class Response(object):
    def __init__(self):
        self.res = {}
        self.update_status("unprocessed")

    def failed(self, message):
        log.error(message)
        self.res["status"] = "failed"
        self.res["message"] = message.lower()

    def unhandled(self, message):
        log.info("Filtered out event: %s", message)
        self.res["status"] = "unhandled"
        self.res["message"] = message.lower()

    @property
    def is_unhandled(self):
        return self.res.get("result", {}).get("status") == "unhandled"

    def update_status(self, status, message=None):
        self.res.setdefault("result", {})['status'] = status
        if message is not None:
            self.res['result']["message"] = message
        elif "message" in self.res:
            del self.res['result']["message"]

    @property
    def successful(self):
        return self.res.setdefault("result", {}).get("status") == "succeeded"

    def toDict(self):
        return self.res

    @property
    def request_type(self):
        return self.res.get("request", {}).get("type", None)

    @request_type.setter
    def request_type(self, tt):
        self.res.setdefault("request", {})["type"] = tt

    @property
    def request_event(self):
        return self.res.get("request", {}).get("event", None)

    @request_event.setter
    def request_event(self, ee):
        self.res.setdefault("request", {})["event"] = ee

    @property
    def exception(self):
        return self.res.get("result", {}).get("exception", None)

    @exception.setter
    def exception(self, ee):
        self.res.setdefault("result", {})["exception"] = ee

    @property
    def subtitles(self):
        return self.res.get("result", {}).get("subtitles", None)

    @subtitles.setter
    def subtitles(self, ee):
        self.res.setdefault("result", {})["subtitles"] = ee

    @property
    def candidates(self):
        return self.res.setdefault("candidates", [])

    @candidates.setter
    def candidates(self, ee):
        self.res.candidates = ee

    @property
    def sonarr_summary(self):
        candidate = self.candidates[0]
        subtitles = self.subtitles
        return [{
            "series_title": candidate.get("series_title"),
            "season_number": candidate.get("season_number"),
            "episode_number": candidate.get("episode_number"),
            "quality": candidate.get("quality"),
            "video_languages": candidate.get("video_languages", "???"),
            "subtitles_languages": ",".join(s["language"] for s in subtitles),
        }]
