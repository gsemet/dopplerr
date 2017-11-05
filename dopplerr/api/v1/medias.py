# coding: utf-8

import logging

from sanic import Blueprint
from sanic_transmute import add_route
from sanic_transmute import describe
from schematics.models import Model

from dopplerr.downloader import DopplerrDownloader

log = logging.getLogger(__name__)


class RequestAnswer(Model):
    pass


bp = Blueprint('medias', url_prefix="/api/v1")


@describe(paths="/medias/", methods="GET")
async def fullscan(request) -> RequestAnswer:
    content = request.json
    logging.debug("Fullscan request: %r", content)
    res = DopplerrDownloader().process_fullscan(content)
    res = "Unimplemented"
    return res


add_route(bp, fullscan)
