# coding: utf-8

import asyncio
import logging
import time

from asynctest import TestCase

from dopplerr.tasks.manager import DopplerrTasksManager
from dopplerr.tasks.threaded import ThreadedTask

log = logging.getLogger(__name__)


class SingleExecutor(ThreadedTask):
    worker_threads_num = 1

    async def execute(self, long_task, *args):
        return await self._run_in_thread(long_task, *args)

    async def _run(self, task):
        raise NotImplementedError


class TestApscheduler(TestCase):
    async def test_executors(self):
        log.info("")
        de = DopplerrTasksManager()

        def mkprefix(i):
            return " " * 15 + " " * 45 * i

        def long_sync_task(i):
            # all tasks should run inside the SAME thread
            prefix = mkprefix(1)
            log.info(prefix + "long  sync task %s: begin", i)
            for _ in range(0, i * 10):
                log.info(prefix + "long  sync task %s: working", i)
                # note: time.sleep does NOT block current thread, so other "blocking" task
                # might actually overlap their executions
                time.sleep(0.1)
            log.info(prefix + "long  sync task %s: end", i)

        async def long_async_task(i):
            log.info("long async task %s: begin", i)
            await SingleExecutor().execute(long_sync_task, i)
            log.info("long async task %s: more work after results from run in thread task", i)
            await asyncio.sleep(1)
            log.info("long async task %s: end", i)

        log.info("event loop thread" + " " * 40 + "worker thread")
        de.post_task(long_async_task(1))
        de.post_task(long_async_task(2))
        de.post_task(long_async_task(3))
        de.post_task(long_async_task(4))
        log.info("waiting 5s")
        for _ in range(0, 60):
            log.info("-- running long async tasks: %s --", de.status()['background_tasks'])
            await asyncio.sleep(0.1)
        log.info("end of unittest")
