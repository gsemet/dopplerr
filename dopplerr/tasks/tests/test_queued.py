# coding: utf-8

import asyncio
import logging

import asynctest

from dopplerr.tasks.queued import QueuedTask

log = logging.getLogger(__name__)


class MyTask(QueuedTask):
    name = "MyTask"

    def __init__(self):
        super(MyTask, self).__init__()
        self.input_processed = []
        self.event_sequence = []

    def add_event(self, event, *args):
        log.info(event, *args)
        self.event_sequence.append(event % args)

    async def _run(self, task):
        self.add_event("Task %s: work started", task)
        await asyncio.sleep(0.2)
        self.input_processed.append(task)
        self.add_event("Task %s: work finished", task)
        return "finished task {}".format(task)


class TestTaskQueue(asynctest.TestCase):
    maxDiff = None

    async def test_fire_and_forget(self):
        task = MyTask()
        task.start()
        await task.fire_and_forget("#1")
        await task.fire_and_forget("#2")
        task.add_event("EventLoop: doing other stuff...")
        await asyncio.sleep(1)
        await task.fire_and_forget("#3")
        await task.fire_and_forget("#4")
        task.add_event("EventLoop: doing other other stuff...")
        await asyncio.sleep(1)
        await task.fire_and_forget("maybe unprocessed task")
        task.add_event("EventLoop: stopping everything...")
        await asyncio.sleep(1)
        # await task.join()
        task.stop()
        self.assertIn('#1', task.input_processed)
        self.assertIn('#2', task.input_processed)
        self.assertIn('#3', task.input_processed)
        self.assertIn('#4', task.input_processed)
        self.assertListEqual([
            'EventLoop: doing other stuff...',
            'Task #1: work started',
            'Task #1: work finished',
            'Task #2: work started',
            'Task #2: work finished',
            'EventLoop: doing other other stuff...',
            'Task #3: work started',
            'Task #3: work finished',
            'Task #4: work started',
            'Task #4: work finished',
            'EventLoop: stopping everything...',
            'Task maybe unprocessed task: work started',
            'Task maybe unprocessed task: work finished',
        ], task.event_sequence)

    async def test_run_with_additional_work(self):
        async def job_with_task_and_additional_work(task, task_id):
            task.add_event("Job %s: asking to execute the sequential task", task_id)
            res = await task.run_and_wait(task_id)
            task.add_event("Job %s: result received '%s'", task_id, res)
            task.add_event("Job %s: additional work start (can be executed in //)", task_id)
            await asyncio.sleep(0.4)
            task.add_event("Job %s: additional work end", task_id)

        task = MyTask()
        task.start()
        task.add_event("EventLoop: launching 2 tasks that should be executed sequentially later...")
        asyncio.ensure_future(job_with_task_and_additional_work(task, "#1"))
        asyncio.ensure_future(job_with_task_and_additional_work(task, "#2"))
        task.add_event("EventLoop: doing other other stuff...")
        await asyncio.sleep(1)
        task.stop()
        self.assertListEqual([
            'EventLoop: launching 2 tasks that should be executed sequentially later...',
            'EventLoop: doing other other stuff...',
            'Job #1: asking to execute the sequential task',
            'Job #2: asking to execute the sequential task',
            'Task #1: work started',
            'Task #1: work finished',
            'Task #2: work started',
            "Job #1: result received 'finished task #1'",
            'Job #1: additional work start (can be executed in //)',
            'Task #2: work finished',
            "Job #2: result received 'finished task #2'",
            'Job #2: additional work start (can be executed in //)',
            'Job #1: additional work end',
            'Job #2: additional work end',
        ], task.event_sequence)
