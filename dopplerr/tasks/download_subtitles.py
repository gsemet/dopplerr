# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from pathlib import Path

from dopplerr.db import DopplerrDb
from dopplerr.downloader import DopplerrDownloader

log = logging.getLogger(__name__)


async def download_missing_subtitles(res):
    candidates = res.candidates
    if not candidates:
        DopplerrDb().insert_event("error", "event handled but no candidate found")
        log.debug("event handled but no candidate found")
        res.failed("event handled but no candidate found")
        return res

    for candidate in candidates:
        log.info(
            "Searching episode '%s' from series '%s'. Filename: %s",
            candidate.get("episode_title"),
            candidate.get("series_title"),
            candidate.get("scenename"),
        )
        DopplerrDb().insert_event("availability", "Available: {} - {}x{} - {} [{}].".format(
            candidate.get("series_title"),
            candidate.get("season_number"),
            candidate.get("episode_number"),
            candidate.get("episode_title"),
            candidate.get("quality"),
        ))

        video_files_found = DopplerrDownloader().search_file(candidate['root_dir'],
                                                             candidate['scenename'])
        log.debug("All found files: %r", video_files_found)
        if not video_files_found:
            res.failed("candidates found but no video file found")
            DopplerrDb().insert_event("subtitles", "No video file found for sonarr notification")
            return res
        DopplerrDb().update_series_media(
            series_title=candidate.get("series_title"),
            tv_db_id=candidate.get("tv_db_id"),
            season_number=candidate.get("season_number"),
            episode_number=candidate.get("episode_number"),
            episode_title=candidate.get("episode_title"),
            quality=candidate.get("quality"),
            video_languages=None,
            media_filename=video_files_found[0],
            dirty=True)

        await DopplerrDownloader().download_missing_subtitles(res, video_files_found)
        subtitles = res.subtitles
        if not subtitles:
            DopplerrDb().insert_event("subtitles", "no subtitle found for: {}".format(
                ", ".join([Path(f).name for f in video_files_found])))
            return res
        DopplerrDb().insert_event("subtitles", "subtitles fetched: {}".format(
            ", ".join([
                "{} (lang: {}, source: {})".format(
                    s.get("filename"),
                    s.get("language"),
                    s.get("provider"),
                ) for s in subtitles
            ])))
    return res
