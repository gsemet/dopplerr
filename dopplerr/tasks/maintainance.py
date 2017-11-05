# coding: utf-8

import logging

from dopplerr.singleton import singleton

log = logging.getLogger(__name__)


class PeriodicMaintainanceTask(object):
    job_id = NotImplementedError
    job_type = 'interval'
    job_default_kwargs = {'max_instances': 1}
    scheduler = None
    seconds = None

    async def run(self):
        raise NotImplementedError

    @property
    def _add_job_kwargs(self):
        kw = self.job_default_kwargs.copy()
        if self.seconds:
            kw.update({'seconds': self.seconds})
        return kw

    @property
    def job(self):
        if self.scheduler:
            return self.scheduler.get_job(self.job_id)

    def add_job(self, scheduler):
        self.scheduler = scheduler
        scheduler.add_job(
            self.run, self.job_type, id=self.job_id, replace_existing=True, **self._add_job_kwargs)

    @property
    def next_run_time(self):
        job = self.job
        if job:
            return self.job.next_run_time

    @property
    def next_run_time_iso(self):
        t = self.next_run_time
        if t:
            return t.isoformat()

    @property
    def interval(self):
        return self.seconds

    @property
    def started(self):
        return self.scheduler


@singleton
class ScanDisk(PeriodicMaintainanceTask):
    job_id = 'scan_disk'
    seconds = 10

    async def run(self):
        job = self.job
        log.debug("next run is scheduler to: %s", job.next_run_time.isoformat())
