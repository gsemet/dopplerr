# coding: utf-8

import logging

from sanic import Blueprint
from sanic_transmute import add_route
from sanic_transmute import describe
from schematics.models import Model
from schematics.types import BooleanType
from schematics.types import IntType
from schematics.types import ListType
from schematics.types import ModelType
from schematics.types import StringType

from dopplerr import APSSCHEDULER_VERSION
from dopplerr import DOPPLERR_VERSION
from dopplerr import PYTHON_VERSION
from dopplerr import SANIC_VERSION
from dopplerr.config import DopplerrConfig
from dopplerr.status import DopplerrStatus
from dopplerr.tasks.manager import DopplerrTasksManager

log = logging.getLogger(__name__)


class SubtitleDownloader(Model):
    active = IntType()
    started = IntType()


class DiscScanner(Model):
    interval_sec = IntType()
    next_run_time = StringType()
    active = IntType()
    started = IntType()


class TaskStatus(Model):
    downloader = StringType()
    background_tasks = IntType()
    subtitle_downloader = ModelType(SubtitleDownloader)
    disc_scanner = ModelType(DiscScanner)


class Health(Model):
    healthy = BooleanType()
    languages = ListType(StringType())
    mapping = ListType(StringType())
    version = StringType()


class Version(StringType):
    pass


class Versions(Model):
    dopplerr = StringType()
    apscheduler = StringType()
    sanic = StringType()
    python = StringType()


class Log(Model):
    timestamp = StringType()
    level = StringType()
    message = StringType()


Logs = ListType(ModelType(Log))

bp = Blueprint('status', url_prefix="/api/v1")


@describe(paths="/health")
async def health() -> Health:
    res_health = {
        "healthy": DopplerrStatus().healthy,
        "languages": DopplerrConfig().get_cfg_value("subliminal.languages"),
        "mapping": DopplerrConfig().get_cfg_value("general.mapping"),
        "version": DOPPLERR_VERSION,
    }
    return res_health


add_route(bp, health)


@describe(paths="/tasks/status")
async def tasks_status() -> TaskStatus:
    res_health = DopplerrTasksManager().status()
    return res_health


add_route(bp, tasks_status)


@describe(paths="/version")
async def api_version() -> Version:
    return DOPPLERR_VERSION


add_route(bp, api_version)


@describe(paths="/versions")
async def api_versions() -> Versions:
    return {
        "dopplerr": DOPPLERR_VERSION,
        "apscheduler": APSSCHEDULER_VERSION,
        "sanic": SANIC_VERSION,
        "python": PYTHON_VERSION,
    }


add_route(bp, api_versions)


@describe(paths="/logs", query_parameters=['limit'])
async def api_log_100(limit: int = 100) -> Logs:
    return await DopplerrStatus().get_logs(limit)


add_route(bp, api_log_100)
