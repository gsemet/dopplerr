# coding: utf-8

import asyncio
import logging

log = logging.getLogger(__name__)


class TaskBase(object):
    worker_threads_num = 1
    active = False

    async def run(self, task):
        self.active = True
        try:
            return await self._run(task)
        finally:
            self.active = False

    async def _run(self, task):
        raise NotImplementedError

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
