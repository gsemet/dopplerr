# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import asyncio
import concurrent
import functools
import logging

from dopplerr.tasks.base import TaskBase

log = logging.getLogger(__name__)


class ThreadedTask(TaskBase):
    worker_threads_num = 1

    def __init__(self):
        self.executors = concurrent.futures.ThreadPoolExecutor(max_workers=self.worker_threads_num)

    async def _run_in_thread(self, func, *args, **kwargs):
        event_loop = asyncio.get_event_loop()
        res = await event_loop.run_in_executor(self.executors,
                                               functools.partial(func, *args, **kwargs))
        return res

    async def _run(self, res):
        raise NotImplementedError
