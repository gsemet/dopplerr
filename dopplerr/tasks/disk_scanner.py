# coding: utf-8

import asyncio
import logging
import os

from dopplerr.config import DopplerrConfig
from dopplerr.singleton import singleton
from dopplerr.tasks.periodic import PeriodicTask

log = logging.getLogger(__name__)

SPEED_LIMIT = 20
SPEED_WAIT_SEC = 0.01


@singleton
class DiskScanner(PeriodicTask):
    job_id = 'scan_disk'
    seconds = 10
    minutes = None
    hours = None

    async def run(self):
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
                log.debug(entry.name)
                if not entry.name.startswith('.'):
                    if entry.is_dir(follow_symlinks=False):
                        await self._scan(entry.path)
                    else:
                        await self._refresh(entry.path)

    async def _refresh(self, filepath):
        log.info("File: %s", filepath)
