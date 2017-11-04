# coding: utf-8

import asyncio
import time

import pytest

from dopplerr.tasks.manager import DopplerrTasksManager
from dopplerr.tasks.threaded import ThreadedTask


class SingleExecutor(ThreadedTask):
    worker_threads_num = 1

    async def execute(self, long_task, *args):
        return await self._run_in_thread(long_task, *args)

    async def _run(self, res):
        raise NotImplementedError


@pytest.mark.asyncio
async def test_executors():
    print("")
    de = DopplerrTasksManager()

    def mkprefix(i):
        return " " * 15 + " " * 45 * i

    def long_sync_task(i):
        # all tasks should run inside the SAME thread
        prefix = mkprefix(1)
        print(prefix + "long  sync task {}: begin".format(i))
        for _ in range(0, i * 10):
            print(prefix + "long  sync task {}: working".format(i))
            # note: time.sleep does NOT block current thread, so other "blocking" task
            # might actually overlap their executions
            time.sleep(0.1)
        print(prefix + "long  sync task {}: end".format(i))

    async def long_async_task(i):
        print("long async task {}: begin".format(i))
        await SingleExecutor().execute(long_sync_task, i)
        print("long async task {}: more work after results from run in thread task".format(i))
        await asyncio.sleep(1)
        print("long async task {}: end".format(i))

    print("event loop thread" + " " * 40 + "worker thread")
    de.post_task(long_async_task(1))
    de.post_task(long_async_task(2))
    de.post_task(long_async_task(3))
    de.post_task(long_async_task(4))
    print("waiting 5s")
    for _ in range(0, 60):
        print("-- running long async tasks: {} --".format(de.status()['background_tasks']))
        await asyncio.sleep(0.1)
    print("end of unittest")
