# coding: utf-8

import glob
import logging
import os
from pathlib import Path

from dopplerr.config import DopplerrConfig
from dopplerr.db import DopplerrDb
from dopplerr.singleton import singleton
from dopplerr.status import DopplerrStatus
from dopplerr.tasks.queued import QueuedTask
from dopplerr.tasks.subtasks.subliminal import SubliminalTask

log = logging.getLogger(__name__)


@singleton
class DownloadSubtitleTask(QueuedTask):
    name = "Download Subtitle Task"

    async def _run(self, task):
        log.debug("Starting Download subtitle for task")
        res = task
        if not res.candidates:
            DopplerrDb().insert_event("error", "event handled but no candidate found")
            log.debug("event handled but no candidate found")
            res.failed("event handled but no candidate found")
            return res

        for candidate in res.candidates:
            await self._process_candidate(candidate, res)
        return res

    @staticmethod
    def search_file(root_dir, base_name):
        # This won't work with python < 3.5
        found = []
        base_name = glob.escape(base_name)
        beforext, _, ext = base_name.rpartition('.')
        protected_path = os.path.join(root_dir, "**", "*" + beforext + "*" + '.' + ext)
        protected_path = protected_path
        log.debug("Searching %r", protected_path)
        for filename in glob.iglob(protected_path, recursive=True):
            log.debug("Found: %s", filename)
            found.append(filename)
        return found

    async def _process_candidate(self, candidate, res):
        log.info(
            "Searching episode '%s' from series '%s'. Filename: %s",
            candidate.get("episode_title"),
            candidate.get("series_title"),
            candidate.get("scenename"),
        )

        candidate_files = self._search_candidate_files(candidate, res)
        if not candidate_files:
            return

        self._refresh_db_media(candidate, candidate_files[0])

        videos = self.filter_video_files(candidate_files, res)
        if not videos:
            return

        subtitles_info = await self.download_sub(videos, res)
        res.subtitles = subtitles_info
        if subtitles_info:
            res.successful("download successful")
            DopplerrDb().insert_event("subtitles", "subtitles fetched: {}".format(
                ", ".join([
                    "{} (lang: {}, source: {})".format(
                        s.get("filename"),
                        s.get("language"),
                        s.get("provider"),
                    ) for s in subtitles_info
                ])))
        else:
            DopplerrDb().insert_event("subtitles", "no subtitle found for: {}".format(
                ", ".join([Path(f).name for f in candidate_files])))
            res.failed("no subtitle found")

    @staticmethod
    def _refresh_db_media(candidate, media_filename):
        DopplerrDb().update_series_media(
            series_title=candidate.get("series_title"),
            tv_db_id=candidate.get("tv_db_id"),
            season_number=candidate.get("season_number"),
            episode_number=candidate.get("episode_number"),
            episode_title=candidate.get("episode_title"),
            quality=candidate.get("quality"),
            video_languages=None,
            media_filename=media_filename,
            dirty=True)

    def _search_candidate_files(self, candidate, res):
        candidate_files = self.search_file(candidate['root_dir'], candidate['scenename'])
        log.debug("All found files: %r", candidate_files)
        if not candidate_files:
            res.failed("candidates defined in request but no video file found on disk")
            DopplerrDb().insert_event("subtitles", "No video file found on disk "
                                      "after sonarr notification")
            return []
        return candidate_files

    @staticmethod
    def filter_video_files(candidate_files, res):
        log.info("Searching and downloading missing subtitles for: %r", candidate_files)
        res.processing("downloading missing subtitles")
        videos = SubliminalTask.filter_video_files(candidate_files)
        log.info("Video files: %r", videos)
        if not videos:
            log.debug("No subtitle to download")
            res.failed("no video file found")
            return
        return videos

    async def download_sub(self, videos, res):
        res.processing("fetching best subtitles")
        log.info("fetching subtitles...")
        subtitles = []
        try:
            subliminal = SubliminalTask()
            provider_configs = DopplerrStatus().subliminal_provider_configs
            languages = DopplerrConfig().get_cfg_value("subliminal.languages")
            subtitles = await subliminal.download_sub(
                videos, languages, provider_configs=provider_configs)
        except Exception as e:
            log.exception("subliminal raised an exception")
            res.failed("subliminal exception")
            res.exception = repr(e)
            return res

        subtitles_info = []
        for vid in videos:
            log.info("Found subtitles for %s:", vid)
            for sub in subtitles[vid]:
                log.info("  %s from %s", sub.language, sub.provider_name)
                subtitles_info.append({
                    "language": str(sub.language),
                    "provider": sub.provider_name,
                    "filename": subliminal.get_subtitle_path(vid.name, language=sub.language)
                })
            subliminal.save_subtitles(vid, subtitles[vid])

        return subtitles_info
