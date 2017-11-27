# coding: utf-8

# Standard Libraries
import logging

# Third Party Libraries
from sanic import Blueprint
from schematics.models import Model
from schematics.types import BooleanType
from schematics.types import IntType
from schematics.types import ListType
from schematics.types import ModelType
from schematics.types import StringType

# Dopplerr
from dopplerr import APSSCHEDULER_VERSION
from dopplerr import DOPPLERR_VERSION
from dopplerr import PYTHON_VERSION
from dopplerr import SANIC_VERSION
from dopplerr.api.add_route import describe_add_route
from dopplerr.status import DopplerrStatus
from dopplerr.tasks.disk_scanner import DiskScanner
from dopplerr.tasks.manager import DopplerrTasksManager

log = logging.getLogger(__name__)


class SubtitleDownloader(Model):
    active = IntType()
    started = IntType()


class DiscScanner(Model):
    interval_hours = IntType()
    next_run_time = StringType()
    active = IntType()
    started = IntType()


class TaskStatus(Model):
    downloader = StringType()
    background_tasks = IntType()
    subtitle_downloader = ModelType(SubtitleDownloader)
    disc_scanner = ModelType(DiscScanner)


class Status(Model):
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
    logger = StringType()


OkKo = StringType(regex=r"(OK|KO)")

Logs = ListType(ModelType(Log))

bp = Blueprint('status', url_prefix="/api/v1")


@describe_add_route(bp, paths="/health")
async def health() -> OkKo:
    """
    Health check.

    If it returns KO, Dopplerr is dead and should be restarted.
    """
    return "OK" if DopplerrStatus().healthy else "KO"


@describe_add_route(bp, paths="/ready")
async def ready() -> OkKo:
    """
    Readiness check.

    Use this endpoint to test if Dopplerr can still process new requests. If it
    returns "KO", Dopplerr is either congestionned either starting, and cannot accept
    new requests.
    """
    return "OK" if DopplerrStatus().ready else "KO"


@describe_add_route(bp, paths="/tasks/status")
async def tasks_status() -> TaskStatus:
    res_health = DopplerrTasksManager().status()
    return res_health


@describe_add_route(bp, paths="/tasks/scanner/start", methods=["POST"])
async def start_scanner() -> TaskStatus:
    await DiskScanner().force_start()
    return "OK"


@describe_add_route(bp, paths="/version")
async def api_version() -> Version:
    return DOPPLERR_VERSION


@describe_add_route(bp, paths="/versions")
async def api_versions() -> Versions:
    return {
        "dopplerr": DOPPLERR_VERSION,
        "apscheduler": APSSCHEDULER_VERSION,
        "sanic": SANIC_VERSION,
        "python": PYTHON_VERSION,
    }


@describe_add_route(bp, paths="/logs", query_parameters=['limit'])
async def api_log_100(limit: int = 100) -> Logs:
    return await DopplerrStatus().get_logs(limit)
