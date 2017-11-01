# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from sanic import Blueprint
from sanic.response import text, json

from dopplerr import DOPPLERR_VERSION
from dopplerr.config import DopplerrConfig
from dopplerr.db import DopplerrDb
from dopplerr.downloader import DopplerrDownloader
from dopplerr.tasks.sonarr_on_download import process_sonarr_on_download
from dopplerr.status import DopplerrStatus

log = logging.getLogger(__name__)

bp = Blueprint('api')


@bp.route("/api/v1/recent/events/<num>")
async def recent_events_num(request, num=10):
    num = int(num)
    if num > 100:
        num = 100
    res = {"events": DopplerrDb().get_recent_events(num)}
    return json(res)


@bp.route("/api/v1/recent/events/")
async def recent_events_10(request):
    res = {"events": DopplerrDb().get_recent_events(10)}
    return json(res)


@bp.route("/api/v1/recent/fetched/series/<num>")
async def recent_fetched_series_num(request, num=10):
    num = int(num)
    if num > 100:
        num = 100
    res = {"events": DopplerrDb().get_last_fetched_series(num)}
    return json(res)


@bp.route("/api/v1/notify/sonarr", methods=['POST'])
async def notify_sonarr(request):
    res = await process_sonarr_on_download(request.json)
    return json(res)


@bp.route("/api/v1/notify", methods=['GET'])
async def notify_not_allowed(_request):
    return text(
        "Method GET not allowed. Use POST with a JSON body with the right format",
        status=405,
    )


@bp.route("/api/v1/health")
async def health(request):
    res_health = {
        "healthy": DopplerrStatus().healthy,
        "languages": DopplerrConfig().get_cfg_value("subliminal.languages"),
        "mapping": DopplerrConfig().get_cfg_value("general.mapping"),
        "version": DOPPLERR_VERSION,
    }
    return json(res_health)


@bp.route("/api/v1/version")
async def version(_request):
    return text(DOPPLERR_VERSION)


@bp.route("/api/v1/fullscan")
async def fullscan(request):
    content = request.json
    logging.debug("Fullscan request: %r", content)
    res = await DopplerrDownloader().process_fullscan(content)
    return json(res)


@bp.route("/api/v1/medias/series/")
async def medias_series(request):
    res = {"medias": DopplerrDb().get_medias_series()}
    return json(res)
