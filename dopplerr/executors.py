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


@singleton
class DopplerrExecutors(object):
    def __init__(self):
        self.executors = concurrent.futures.ThreadPoolExecutor(10)

    async def run(self, func, *args, **kwargs):
        event_loop = asyncio.get_event_loop()
        res = await event_loop.run_in_executor(self.executors,
                                               functools.partial(func, *args, **kwargs))
        return res
