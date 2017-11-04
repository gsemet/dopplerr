# coding: utf-8

from enum import Enum
from json import JSONEncoder
from json import dumps


def _pretty_kw():
    return {
        "sort_keys": True,
        "indent": 4,
        "separators": (',', ': '),
    }


class _EnumEncoder(JSONEncoder):
    def default(self, obj):  # pylint: disable=arguments-differ,method-hidden
        if isinstance(obj, Enum):
            return obj.name
        return JSONEncoder.default(self, obj)


def safe_dumps(data):
    return dumps(data, cls=_EnumEncoder, **_pretty_kw())
