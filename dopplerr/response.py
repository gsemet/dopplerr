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
        self.res.setdefault("result", {})["status"] = "failed"
        self.res.setdefault("result", {})["message"] = message.lower()

    def unhandled(self, message):
        log.info("Filtered out event: %s", message)
        self.res.setdefault("result", {})["status"] = "unhandled"
        self.res.setdefault("result", {})["message"] = message.lower()

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

    def to_dict(self):
        return self.res

    @property
    def request_type(self):
        return self.res.get("request", {}).get("type", None)

    @request_type.setter
    def request_type(self, thetype):
        self.res.setdefault("request", {})["type"] = thetype

    @property
    def request_event(self):
        return self.res.get("request", {}).get("event", None)

    @request_event.setter
    def request_event(self, event):
        self.res.setdefault("request", {})["event"] = event

    @property
    def exception(self):
        return self.res.get("result", {}).get("exception", None)

    @exception.setter
    def exception(self, exception):
        self.res.setdefault("result", {})["exception"] = exception

    @property
    def subtitles(self):
        return self.res.get("result", {}).get("subtitles", None)

    @subtitles.setter
    def subtitles(self, subtitles):
        self.res.setdefault("result", {})["subtitles"] = subtitles

    @property
    def candidates(self):
        return self.res.setdefault("candidates", [])

    @candidates.setter
    def candidates(self, candidates):
        self.res.candidates = candidates

    @property
    def sonarr_episode_infos(self):
        candidate = self.candidates[0]
        subtitles = self.subtitles
        return [{
            "series_title": candidate.get("series_title"),
            "season_number": candidate.get("season_number"),
            "tv_db_id": candidate.get("tv_db_id"),
            "episode_number": candidate.get("episode_number"),
            "episode_title": candidate.get("episode_title"),
            "quality": candidate.get("quality"),
            "video_languages": candidate.get("video_languages", "???"),
            "subtitles_languages": [s["language"] for s in subtitles],
        }]
