# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import asyncio
import logging

from txwebbackendbase.singleton import singleton

log = logging.getLogger(__name__)


@singleton
class DopplerrTaskManager():
    def add_task(self, task):
        loop = asyncio.get_event_loop()
        loop.create_task(task)
