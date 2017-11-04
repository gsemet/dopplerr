# -*- coding: utf-8 -*-

import asyncio

from dopplerr.tasks.base import TaskBase


class QueuedTask(TaskBase):
    """
    Task that should be queued, ie, where two similar cannot be executed at the same time,
    but to an underlying shared resource.
    """
    _queue = asyncio.Queue(1000)

    async def _run(self, res):
        raise NotImplementedError
