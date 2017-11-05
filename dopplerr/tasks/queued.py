# coding: utf-8

import asyncio
import logging

from dopplerr.tasks.base import TaskBase

log = logging.getLogger(__name__)


class QueuedTask(TaskBase):
    """
    Task that should be queued, ie, where two similar cannot be executed at the same time,
    but to an underlying shared resource.

    Usage:

    - inherit from `QueuedTask` and implement `name` member and `_run` methods

        class MyTask(QueuedTask):
            name = "MyTask"

            async def _run(self, task):
                ...

    """
    _queue = None
    _result = None
    _started = False
    _consumer = None
    name = "Unnamed queue"
    FIRE_AND_FORGET = 0
    WAIT_FOR_RESULT = 1

    def __init__(self):
        self._queue = asyncio.Queue()
        self._result = asyncio.Queue()

    async def _loop_queue(self):
        assert self._queue
        while True:
            # log.debug("QueuedTask %s: waits for something in the task queue", self.name)
            fire_and_forget, inputs = await self._queue.get()

            try:
                self.active = True
                # log.debug("QueuedTask %s: starts execution: %r", self.name, inputs)
                result = await self._run(inputs)
                # log.debug("QueuedTask %s: ends execution: %r (result: %r)", self.name, inputs,
                #           result)
                if fire_and_forget == QueuedTask.WAIT_FOR_RESULT:
                    # log.debug("QueuedTask %s: task %s is 'wait for result', posting result %r",
                    #           self.name, inputs, result)
                    await self._result.put(result)
            finally:
                self.active = False
                self._queue.task_done()

    async def _run(self, task):
        raise NotImplementedError

    async def _wait_next_result(self):
        assert self.started
        # log.debug("QueuedTask %s: waiting for result", self.name)
        r = await self._result.get()
        # log.debug("QueuedTask %s: previous task returned a result: %s", self.name, r)
        self._result.task_done()
        return r

    def start(self):
        assert self._queue
        if self.stopped:
            # log.debug("QueuedTask %s: starting queue", self.name)
            self._consumer = asyncio.ensure_future(self._loop_queue())

    def stop(self):
        assert self._queue
        # log.debug("QueuedTask %s: stopping queue", self.name)
        if self._consumer:
            self._consumer.cancel()
        self._consumer = None

    async def fire_and_forget(self, task):
        assert self._queue
        # log.debug("QueuedTask %s: posting new execution request: %r", self.name, task)
        await self._queue.put((QueuedTask.FIRE_AND_FORGET, task))

    async def run(self, task):
        return await self.run_and_wait(task)

    async def run_and_wait(self, task):
        assert self._queue
        # log.debug("QueuedTask %s: posting 'Run and resume' job: %r", self.name, task)
        await self._queue.put((QueuedTask.WAIT_FOR_RESULT, task))
        # log.debug("QueuedTask %s: task %s posted, waiting for result", self.name, task)
        return await self._wait_next_result()

    async def join(self):
        assert self._queue
        await self._queue.join()

    @property
    def stopped(self):
        return not self.started

    @property
    def started(self):
        return self._consumer
