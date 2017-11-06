# coding: utf-8

import asyncio
import logging
import os

from dopplerr.config import DopplerrConfig
from dopplerr.singleton import singleton
from dopplerr.tasks.periodic import PeriodicTask

log = logging.getLogger(__name__)

SPEED_LIMIT = 10
SPEED_WAIT_SEC = 0.1
VIDEO_FILES_EXT = [
    'asf',
    'avc',
    'avi',
    'divx',
    'm4v',
    'mkv',
    'mov',
    'mp4',
    'mpg',
    'ogv',
    'qt',
    'viv',
    'vp3',
    'wmv',
]


@singleton
class DiskScanner(PeriodicTask):
    job_id = 'scan_disk'
    seconds = 10
    minutes = None
    hours = None
    enable_cfg = 'scanner.enable'

    async def _run(self):
        basedir = DopplerrConfig().get_cfg_value('general.basedir')
        log.debug("Scanning %s", basedir)
        await self._scan(basedir)

    async def _scan(self, root):
        i = 0
        with os.scandir(root) as it:
            for entry in it:
                i += 1
                if i > SPEED_LIMIT:
                    # this allows the event loop to update
                    await asyncio.sleep(SPEED_WAIT_SEC)
                    i = 0
                if self.stopped:
                    return
                if not entry.name.startswith('.'):
                    if entry.is_dir(follow_symlinks=False):
                        await self._scan(entry.path)
                    else:
                        if entry.name.rpartition('.')[2] in VIDEO_FILES_EXT:
                            await self._refresh_video(entry.path)

    async def _refresh_video(self, filepath):
        log.info("Video file found: %s", filepath)
