# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import asyncio
import concurrent
import functools
import logging

from dopplerr.singleton import singleton

log = logging.getLogger(__name__)


class TaskBase(object):
    parallel_executors = 1

    def __init__(self):
        self.executors = concurrent.futures.ThreadPoolExecutor(max_workers=self.parallel_executors)

    async def _run_in_thread(self, func, *args, **kwargs):
        event_loop = asyncio.get_event_loop()
        res = await event_loop.run_in_executor(self.executors,
                                               functools.partial(func, *args, **kwargs))
        return res

    @staticmethod
    async def _run_command(*args):
        """
        Asynchronous run command in subprocess

        :param *args: command to execute
        :return: tuple (stdout, stderr, exit code)

        Example from: http://asyncio.readthedocs.io/en/latest/subprocess.html
        """
        # Create subprocess
        log.debug("Executing subprocess: %s", " ".join([a for a in args]))
        # pylint: disable=no-value-for-parameter
        process = await asyncio.create_subprocess_exec(
            *args, stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
        # pylint: enable=no-value-for-parameter

        # Status
        log.info('Started: %s (pid = %s)', args, process.pid)

        # Wait for the subprocess to finish
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            log.debug('Subprocess pid %s succeeded: %s', process.pid, args)
        else:
            log.debug('Subprocess pid %s failed: %s', process.pid, args)

        stdout_str = stdout.decode().strip()
        stderr_str = stderr.decode().strip()

        # Return stdout, stderr, exit code
        return stdout_str, stderr_str, process.returncode


@singleton
class DopplerrExecutors(object):
    background_tasks = 0

    def post_task(self, task):
        """
        TODO: transfor this simple wrapper arround `create_task ` into a real queue management
        """

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
