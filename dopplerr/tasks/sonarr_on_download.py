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
from dopplerr.notifications import emit_notifications
from dopplerr.notifications_types.series_subtitles_fetched import SubtitleFetchedNotification
from dopplerr.request_filter import SonarrFilter
from dopplerr.response import Response

log = logging.getLogger(__name__)


@singleton
class Executors(object):
    def __init__(self):
        self.executors = concurrent.futures.ThreadPoolExecutor(10)

class SonarrOnDownloadResponse(object):
    pass

def _process_sonarr_on_download(content):
    logging.debug("Sonarr notification received: %r", content)
    res = SonarrOnDownloadResponse()

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


async def process_sonarr_on_download(content):
    event_loop = asyncio.get_event_loop()
    res = await event_loop.run_in_executor(Executors().executors, _process_sonarr_on_download, content)
    log.debug("Successful: %r", res.successful)
    if not res.successful:
        return json(res.to_dict())
    for episode_info in res.sonarr_episode_infos:
        await emit_notifications(SubtitleFetchedNotification(series_episode_info=episode_info))
        DopplerrDb().update_fetched_series_subtitles(
            series_episode_uid=episode_info.series_episode_uid,
            subtitles_languages=episode_info.subtitles_languages,
            dirty=False)
    return json(res.to_dict())
