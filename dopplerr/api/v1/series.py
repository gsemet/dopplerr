# coding: utf-8

import logging

from sanic import Blueprint
from sanic_transmute import add_route
from sanic_transmute import describe
from schematics.models import Model
from schematics.types import DateType
from schematics.types import ListType
from schematics.types import ModelType
from schematics.types import StringType

from dopplerr.db import DopplerrDb

log = logging.getLogger(__name__)

bp = Blueprint('series', url_prefix="/api/v1/medias/series")


class Media(Model):
    timestamp = DateType()
    type = StringType()
    message = StringType()


class Series(Model):
    medias = ListType(ModelType(Media))


@describe(paths="/all", methods="GET")
async def medias_series():
    res = {"medias": DopplerrDb().get_medias_series()}
    return res


add_route(bp, medias_series)
