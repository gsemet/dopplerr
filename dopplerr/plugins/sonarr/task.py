# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from dopplerr.db import DopplerrDb
from dopplerr.notifications import emit_notifications
from dopplerr.notifications_types.series_subtitles_fetched import SubtitleFetchedNotification
from dopplerr.plugins.sonarr.filter import SonarrFilter
from dopplerr.tasks.download_subtitles import download_missing_subtitles
from dopplerr.tasks.task_manager import DopplerrTaskManager

log = logging.getLogger(__name__)


class DopplerrTask(object):
    def add_task(self, task):
        DopplerrTaskManager().add_task(task)


class TaskSonarrOnDownload(DopplerrTask):
    async def run(self, content):

        logging.debug("Sonarr notification received: %r", content)
        res = await SonarrFilter().filter(content)
        if res.is_unhandled:
            # event has been filtered out
            return res

        self.add_task(self.task_sonarr_on_download_background(res))
        return res.to_dict()

    async def task_sonarr_on_download_background(self, res):
        log.debug("Starting task_sonarr_on_download_background")
        res = await download_missing_subtitles(res)
        log.debug("Successful: %r", res.successful)
        if not res.successful:
            return res

        for episode_info in res.sonarr_episode_infos:
            await emit_notifications(SubtitleFetchedNotification(series_episode_info=episode_info))
            DopplerrDb().update_fetched_series_subtitles(
                series_episode_uid=episode_info.series_episode_uid,
                subtitles_languages=episode_info.subtitles_languages,
                dirty=False)
        logging.debug("Background task finished with result: %s", res.to_json())
        return res
