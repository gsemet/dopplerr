# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import asyncio
import concurrent
import logging
from pathlib import Path

from sanic.response import json
from txwebbackendbase.singleton import singleton

from dopplerr.db import DopplerrDb
from dopplerr.downloader import DopplerrDownloader
from dopplerr.notifications import SubtitleFetchedNotification
from dopplerr.notifications import emit_notifications
from dopplerr.request_filter import SonarrFilter
from dopplerr.response import Response

log = logging.getLogger(__name__)


@singleton
class Executors(object):
    def __init__(self):
        self._executors = concurrent.futures.ThreadPoolExecutor(10)


def _process_notify_sonarr(content):
    logging.debug("Notify sonarr request: %r", content)
    log.debug("Processing request: %r", content)
    res = Response()

    SonarrFilter().filter(content, res)
    if res.is_unhandled:
        # event has been filtered out
        return res

    candidates = res.candidates
    if not candidates:
        DopplerrDb().insert_event("error", "event handled but no candidate found")
        log.debug("event handled but no candidate found")
        res.update_status("failed", "event handled but no candidate found")
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
            res.update_status("failed", "candidates found but no video file found")
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

        DopplerrDownloader().download_missing_subtitles(res, video_files_found)
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


async def process_notify_sonarr(content):
    event_loop = asyncio.get_event_loop()
    res = await event_loop.run_in_executor(Executors()._executors, _process_notify_sonarr, content)
    log.debug("Successful: %r", res.successful)
    if not res.successful:
        return json(res.to_dict())
    for st in res.sonarr_summary:
        await emit_notifications(
            SubtitleFetchedNotification(
                series_title=st['series_title'],
                season_number=st['season_number'],
                tv_db_id=st['tv_db_id'],
                episode_number=st['episode_number'],
                episode_title=st['episode_title'],
                quality=st['quality'],
                video_languages=st['video_languages'],
                subtitles_languages=st['subtitles_languages'],
            ))
        DopplerrDb().update_fetched_series_subtitles(
            tv_db_id=st['tv_db_id'],
            season_number=st['season_number'],
            episode_number=st['episode_number'],
            subtitles_languages=st['subtitles_languages'],
            dirty=False,
        )
    return json(res.to_dict())
