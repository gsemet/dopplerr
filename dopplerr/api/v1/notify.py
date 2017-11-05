# coding: utf-8

import logging

from sanic import Blueprint
from sanic_transmute import APIException
from sanic_transmute import add_route
from sanic_transmute import describe

from dopplerr.plugins.sonarr.task import TaskSonarrOnDownload

log = logging.getLogger(__name__)

bp = Blueprint('notify', url_prefix="/api/v1")


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
