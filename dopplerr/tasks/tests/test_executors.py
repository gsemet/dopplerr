# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import asyncio
import time

import pytest

from dopplerr.tasks.executors import DopplerrExecutors
from dopplerr.tasks.executors import _ExecutorsBase


class OnlyOneExecution(_ExecutorsBase):
    parallel_executors = 1


@pytest.mark.asyncio
async def test_executors():
    print("")
    de = DopplerrExecutors()

    def mkprefix(i):
        return " " * 15 + " " * 45 * i

    def long_sync_task(i):
        # all tasks should run inside the SAME thread
        prefix = mkprefix(1)
        print(prefix + "long  sync task {}: begin".format(i))
        for _ in range(0, i * 10):
            print(prefix + "long  sync task {}: working".format(i))
            time.sleep(0.1)
        print(prefix + "long  sync task {}: end".format(i))

    async def long_async_task(i):
        print("long async task {}: begin".format(i))
        await OnlyOneExecution().run_in_thread(long_sync_task, i)
        print("long async task {}: more work after results from run in thread task".format(i))
        await asyncio.sleep(1)
        print("long async task {}: end".format(i))

    print("event loop thread" + " " * 40 + "worker thread")
    de.run_in_background(long_async_task(1))
    de.run_in_background(long_async_task(2))
    de.run_in_background(long_async_task(3))
    de.run_in_background(long_async_task(4))
    print("waiting 5s")
    for _ in range(0, 60):
        print("-- running long async tasks: {} --".format(de.status()['background_tasks']))
        await asyncio.sleep(0.1)
    print("end of unittest")
