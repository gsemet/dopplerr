# coding: utf-8

import logging
from enum import Enum

from dopplerr import json

log = logging.getLogger(__name__)


class RequestStatus(Enum):
    UNHANDLED = "unhandled"
    PROCESSING = "processing"
    SUCCESSFUL = "successful"
    FAILED = "failed"


class Response(object):
    def __init__(self):
        self.res = {}
        self.__update_status(RequestStatus.UNHANDLED)

    def processing(self, message=None):
        self.__update_status(RequestStatus.PROCESSING, message=message)

    def failed(self, message):
        log.error(message)
        self.__update_status(RequestStatus.FAILED, message=message.lower())

    def unhandled(self, message):
        log.info("Filtered out event: %s", message)
        self.res.setdefault("result", {})["status"] = RequestStatus.UNHANDLED
        self.res.setdefault("result", {})["message"] = message.lower()

    @property
    def is_unhandled(self):
        return self.res.get("result", {}).get("status") == RequestStatus.UNHANDLED

    @property
    def is_failed(self):
        return self.res.get("result", {}).get("status") == RequestStatus.FAILED

    def __update_status(self, status, message=None):
        self.res.setdefault("result", {})['status'] = status
        if message is not None:
            self.res['result']["message"] = message
        elif "message" in self.res:
            del self.res['result']["message"]

    def successful(self, message=None):
        return self.__update_status(RequestStatus.SUCCESSFUL, message=message)

    @property
    def is_successful(self):
        return self.res.get("result", {}).get("status") == RequestStatus.SUCCESSFUL

    def to_dict(self):
        """
        Return json-able dictionary
        """
        return self._to_dict(self.res)

    def _to_dict(self, dat):
        r = {}
        for k, v in dat.items():
            if isinstance(v, Enum):
                v = v.name
            elif isinstance(v, dict):
                v = self._to_dict(v)
            r[k] = v
        return r

    def to_json(self):
        return json.safe_dumps(self.res)

    @property
    def request_type(self):
        return self.res.get("request", {}).get("type", None)

    @request_type.setter
    def request_type(self, thetype):
        self.res.setdefault("request", {})["type"] = thetype

    @property
    def request_event(self):
        return self.res.get("request", {}).get("event", None)

    @request_event.setter
    def request_event(self, event):
        self.res.setdefault("request", {})["event"] = event

    @property
    def exception(self):
        return self.res.get("result", {}).get("exception", None)

    @exception.setter
    def exception(self, exception):
        self.res.setdefault("result", {})["exception"] = exception


class UnhandledResponse(Response):
    def __init__(self, message, *args, **kwargs):
        super(UnhandledResponse, self).__init__(*args, **kwargs)
        self.request_type = "sonarr"
        self.request_type = "unhandled"
        self.failed(message)
