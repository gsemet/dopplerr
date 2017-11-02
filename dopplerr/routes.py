# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from pathlib import Path

from sanic import Sanic

from dopplerr.api import v1
from dopplerr.config import DopplerrConfig
from dopplerr.status import DopplerrStatus
from dopplerr.tasks.periodic_task_manager import PeriodicTaskManager

log = logging.getLogger(__name__)


def listen():
    app = Sanic(__name__, log_config=None)
    app.blueprint(v1.bp)

    DopplerrStatus().healthy = True
    for fi in Path(DopplerrConfig().get_cfg_value("general.frontenddir")).iterdir():
        app.static('/' + fi.name if fi.name != "index.html" else '/', fi.resolve().as_posix())
    app.add_task(PeriodicTaskManager().run())
    app.run(host='0.0.0.0', port=int(DopplerrConfig().get_cfg_value("general.port")))
