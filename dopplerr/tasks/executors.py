# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import asyncio
import concurrent
import functools
import logging

from txwebbackendbase.singleton import singleton

log = logging.getLogger(__name__)


class _ExecutorsBase(object):
    parallel_executors = 1

    def __init__(self):
        self.executors = concurrent.futures.ThreadPoolExecutor(max_workers=self.parallel_executors)

    async def run_in_thread(self, func, *args, **kwargs):
        event_loop = asyncio.get_event_loop()
        res = await event_loop.run_in_executor(self.executors,
                                               functools.partial(func, *args, **kwargs))
        return res


class _SubliminalExecutors(_ExecutorsBase):
    parallel_executors = 1


@singleton
class DopplerrExecutors(object):
    background_tasks = 0

    def __init__(self):
        self.subliminal_executors = _SubliminalExecutors()

    def run_in_background(self, task):
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
        }
