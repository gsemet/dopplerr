# coding: utf-8

import asyncio
import logging

from dopplerr.singleton import singleton
from dopplerr.tasks.download_subtitles import DownloadSubtitleTask

log = logging.getLogger(__name__)


@singleton
class DopplerrTasksManager(object):
    background_tasks = 0

    def post_task(self, task):
        """
        TODO: transfor this simple wrapper arround `create_task ` into a real queue management
        """

        async def wrap_task(task):
            self.background_tasks += 1
            res = await task
            self.background_tasks -= 1
            return res

        loop = asyncio.get_event_loop()
        loop.create_task(wrap_task(task))

    def status(self):
        return {
            'background_tasks': self.background_tasks,
            'subtitle_downloader': {
                'active': 1 if DownloadSubtitleTask().active else 0,
            }
        }
