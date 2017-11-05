# coding: utf-8

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dopplerr.singleton import singleton
from dopplerr.tasks.download_subtitles import DownloadSubtitleTask
from dopplerr.tasks.maintainance import ScanDisk

log = logging.getLogger(__name__)


@singleton
class DopplerrTasksManager(object):
    background_tasks = 0
    apscheduler = None

    def post_task(self, task):
        """
        TODO: transfor this simple wrapper arround `create_task ` into a real queue management
        """

        async def wrap_task(task):
            try:
                self.background_tasks += 1
                return await task
            finally:
                self.background_tasks -= 1

        asyncio.ensure_future(wrap_task(task))

    def start(self):
        DownloadSubtitleTask().start()
        self.apscheduler = AsyncIOScheduler()
        ScanDisk().add_job(self.apscheduler)
        self.apscheduler.start()

    def stop(self):
        DownloadSubtitleTask().stop()
        self.apscheduler.shutdown(False)

    def status(self):
        return {
            'background_tasks': self.background_tasks,
            'subtitle_downloader': {
                'started': 1 if DownloadSubtitleTask().started else 0,
                'active': 1 if DownloadSubtitleTask().active else 0,
            },
            'disc_scanner': {
                'started': 1 if ScanDisk().started else 0,
                'interval_sec': ScanDisk().interval,
                'next_run_time': ScanDisk().next_run_time_iso,
            }
        }
