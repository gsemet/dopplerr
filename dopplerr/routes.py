# coding: utf-8

import logging
from pathlib import Path

from sanic import Sanic
from sanic_transmute import add_swagger

from dopplerr.api.v1 import add_api_blueprints
from dopplerr.config import DopplerrConfig
from dopplerr.status import DopplerrStatus

log = logging.getLogger(__name__)


def listen():
    app = Sanic(__name__, log_config=None)
    add_api_blueprints(app)
    add_swagger(app, "/api/v1/swagger.json", "/api/v1/")

    DopplerrStatus().healthy = True
    for fi in Path(DopplerrConfig().get_cfg_value("general.frontenddir")).iterdir():
        app.static('/' + fi.name if fi.name != "index.html" else '/', fi.resolve().as_posix())
    app.run(host='0.0.0.0', port=int(DopplerrConfig().get_cfg_value("general.port")))
