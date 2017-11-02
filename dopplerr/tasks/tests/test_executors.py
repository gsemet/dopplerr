# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import asyncio
import pytest

from unittest import TestCase

from dopplerr.tasks.executors import DopplerrExecutors, _ExecutorsBase

class OnlyOneExecution(_ExecutorsBase):
    parallel_executors = 1

@pytest.mark.asyncio
async def test_executors():
    print("")
    de = DopplerrExecutors()

    async def long_task():
        print("long task")
        await asyncio.sleep(1)
        print("long task finished")

    de.run_in_background(long_task())
    de.run_in_background(long_task())
    de.run_in_background(long_task())
    de.run_in_background(long_task())
    print("waiting 2s")
    await asyncio.sleep(2)
    print("end of unittest")
