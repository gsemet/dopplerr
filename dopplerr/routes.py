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

# pylint: disable=super-init-not-called


class UseMyLoggingSanic(Sanic):
    def __init__(self,
                 name=None,
                 router=None,
                 error_handler=None,
                 load_env=True,
                 request_class=None,
                 strict_slashes=False):

        from collections import deque, defaultdict
        from inspect import stack, getmodulename
        from sanic.router import Router
        from sanic.handlers import ErrorHandler
        from sanic.config import Config

        # Get name from previous stack frame
        if name is None:
            frame_records = stack()[1]
            name = getmodulename(frame_records[1])

        # logging
        # logging.config.dictConfig(log_config or LOGGING_CONFIG_DEFAULTS)
        self.log_config = None

        self.name = name
        self.router = router or Router()
        self.request_class = request_class
        self.error_handler = error_handler or ErrorHandler()
        self.config = Config(load_env=load_env)
        self.request_middleware = deque()
        self.response_middleware = deque()
        self.blueprints = {}
        self._blueprint_order = []
        self.debug = None
        self.sock = None
        self.strict_slashes = strict_slashes
        self.listeners = defaultdict(list)
        self.is_running = False
        self.is_request_stream = False
        self.websocket_enabled = False
        self.websocket_tasks = set()

        # Register alternative method names
        self.go_fast = self.run


# pylint: enable=super-init-not-called


def listen():
    # app = Klein()
    app = UseMyLoggingSanic(__name__)
    app.blueprint(v1.bp)

    DopplerrStatus().healthy = True
    for fi in Path(DopplerrConfig().get_cfg_value("general.frontenddir")).iterdir():
        app.static('/' + fi.name if fi.name != "index.html" else '/', fi.resolve().as_posix())
    app.add_task(PeriodicTaskManager().run())
    app.run(host='0.0.0.0', port=int(DopplerrConfig().get_cfg_value("general.port")))
