# coding: utf-8

import logging

from sanic import Blueprint
from sanic_transmute import APIException
from sanic_transmute import add_route
from sanic_transmute import describe
from schematics.models import Model
from schematics.types import BooleanType
from schematics.types import IntType
from schematics.types import ListType
from schematics.types import ModelType
from schematics.types import StringType

from dopplerr import DOPPLERR_VERSION
from dopplerr.config import DopplerrConfig
from dopplerr.downloader import DopplerrDownloader
from dopplerr.plugins.sonarr.task import TaskSonarrOnDownload
from dopplerr.status import DopplerrStatus
from dopplerr.tasks.manager import DopplerrTasksManager

log = logging.getLogger(__name__)


class SubtitleDownloader(Model):
    active = IntType()
    started = IntType()


class TaskStatus(Model):
    downloader = StringType()
    background_tasks = IntType()
    subtitle_downloader = ModelType(SubtitleDownloader)


class Health(Model):
    healthy = BooleanType()
    languages = ListType(StringType())
    mapping = ListType(StringType())
    version = StringType()


class Version(StringType):
    pass


class RequestAnswer(Model):
    pass


bp = Blueprint('other', url_prefix="/api/v1")


@describe(paths="/notify/sonarr", methods=['POST'])
async def notify_sonarr(request):
    res = await TaskSonarrOnDownload().run(request.json)
    return res


add_route(bp, notify_sonarr)


@describe(paths="/notify", methods=['GET'])
async def notify_not_allowed():
    return APIException(
        "Method GET not allowed. "
        "Use POST with a JSON body with the right format", code=405)


add_route(bp, notify_not_allowed)


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


@describe(paths="/medias/", methods="GET")
async def fullscan(request) -> RequestAnswer:
    content = request.json
    logging.debug("Fullscan request: %r", content)
    res = DopplerrDownloader().process_fullscan(content)
    res = "Unimplemented"
    return res


add_route(bp, fullscan)
