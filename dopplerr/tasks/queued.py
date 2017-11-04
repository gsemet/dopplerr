# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

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
