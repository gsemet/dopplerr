# coding: utf-8

import logging

from dopplerr.response import Response

log = logging.getLogger(__name__)


class SonarrOnDownloadResponse(Response):
    def __init__(self, *args, **kwargs):
        super(SonarrOnDownloadResponse, self).__init__(*args, **kwargs)
        self.request_type = "sonarr"
        self.request_event = "on download"

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
            "tv_db_id": candidate.get("tv_db_id"),
            "season_number": candidate.get("season_number"),
            "episode_number": candidate.get("episode_number"),
            "episode_title": candidate.get("episode_title"),
            "quality": candidate.get("quality"),
            "video_languages": candidate.get("video_languages", "???"),
            "subtitles_languages": [s["language"] for s in subtitles],
        }]
