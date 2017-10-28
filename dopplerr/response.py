# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

log = logging.getLogger(__name__)


class Response(object):
    def __init__(self):
        self.res = {}
        self.update_status("unprocessed")

    def failed(self, message):
        log.error(message)
        self.res["status"] = "failed"
        self.res["message"] = message.lower()

    def unhandled(self, message):
        log.information("Filtered out event: %s", message)
        self.res["status"] = "unhandled"
        self.res["message"] = message.lower()

    @property
    def is_unhandled(self):
        return self.get("status") == "unhandled"

    def update_status(self, status, message=None):
        self.res["status"] = status
        if message is not None:
            self.res["message"] = message
        elif "message" in self.res:
            del self.res["message"]

    def set(self, key, value):
        self.res[key] = value

    def get(self, key, default=None):
        return self.res.get(key, default)

    def setdefault(self, key, default):
        return self.res.setdefault(key, default)

    def toDict(self):
        return self.res
