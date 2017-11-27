# coding: utf-8

# Standard Libraries
import logging

# Third Party Libraries
from sanic import Blueprint
from schematics.models import Model

# Dopplerr
from dopplerr.api.add_route import describe_add_route
from dopplerr.downloader import DopplerrDownloader

log = logging.getLogger(__name__)


class RequestAnswer(Model):
    pass


bp = Blueprint('medias', url_prefix="/api/v1")


@describe_add_route(bp, paths="/medias/", methods="GET")
async def fullscan(request) -> RequestAnswer:
    content = request.json
    logging.debug("Fullscan request: %r", content)
    res = DopplerrDownloader().process_fullscan(content)
    res = "Unimplemented"
    return res
