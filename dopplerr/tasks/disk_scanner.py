# coding: utf-8

import logging

from dopplerr.singleton import singleton
from dopplerr.tasks.periodic import PeriodicTask

log = logging.getLogger(__name__)


@singleton
class DiskScanner(PeriodicTask):
    job_id = 'scan_disk'
    seconds = 10
    minutes = None
    hours = None

    async def run(self):
        job = self.job
        log.debug("next run is scheduler to: %s", job.next_run_time.isoformat())
