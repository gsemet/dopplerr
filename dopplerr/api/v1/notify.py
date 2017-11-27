# coding: utf-8

# Standard Libraries
import logging

# Third Party Libraries
from sanic import Blueprint
from sanic_transmute import APIException

# Dopplerr
from dopplerr.api.add_route import describe_add_route
from dopplerr.plugins.sonarr.task import TaskSonarrOnDownload

log = logging.getLogger(__name__)

bp = Blueprint('notify', url_prefix="/api/v1")


@describe_add_route(bp, paths="/notify/sonarr", methods=['POST'])
async def notify_sonarr(request):
    """
    Process a sonarr notification.
    """
    res = await TaskSonarrOnDownload().run(request.json)
    return res


@describe_add_route(bp, paths="/notify", methods=['GET'])
async def notify_not_allowed():
    return APIException(
        "Method GET not allowed. "
        "Use POST with a JSON body with the right format", code=405)
