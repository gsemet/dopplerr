# coding: utf-8

import logging
from pathlib import Path

from sanic import Sanic
from sanic_transmute import add_swagger

from dopplerr.api.v1 import add_api_blueprints
from dopplerr.config import DopplerrConfig
from dopplerr.status import DopplerrStatus
from dopplerr.tasks.manager import DopplerrTasksManager

log = logging.getLogger(__name__)


async def init_in_sanic_loop():
    DopplerrTasksManager().start()


async def deinit_in_sanic_loop():
    DopplerrTasksManager().stop()


def listen():
    app = Sanic(__name__, log_config=None)
    add_api_blueprints(app)
    add_swagger(app, "/api/v1/swagger.json", "/api/v1/")

    DopplerrStatus().healthy = True
    for fi in Path(DopplerrConfig().get_cfg_value("general.frontenddir")).iterdir():
        app.static('/' + fi.name if fi.name != "index.html" else '/', fi.resolve().as_posix())

    @app.listener('before_server_start')
    async def before_start(_app, _loop):  # pylint: disable=unused-variable
        await init_in_sanic_loop()

    @app.listener('after_server_stop')
    async def after_stop(_app, _loop):  # pylint: disable=unused-variable
        await deinit_in_sanic_loop()

    app.run(host='0.0.0.0', port=int(DopplerrConfig().get_cfg_value("general.port")))
