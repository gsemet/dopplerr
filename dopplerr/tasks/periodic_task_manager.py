# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import asyncio
import logging

from dopplerr.singleton import singleton

log = logging.getLogger(__name__)


@singleton
class PeriodicTaskManager(object):
    running = True

    async def run(self):
        while self.running:
            await asyncio.sleep(2)
            if not self.running:
                return
            log.debug("PERIODIC TASK MANAGER !!!!")

    def stop(self):
        self.running = False
