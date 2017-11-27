# coding: utf-8

# Standard Libraries
import logging

# Third Party Libraries
from sanic import Blueprint
from schematics.models import Model
from schematics.types import DateType
from schematics.types import IntType
from schematics.types import ListType
from schematics.types import ModelType
from schematics.types import StringType

# Dopplerr
from dopplerr.api.add_route import describe_add_route
from dopplerr.db import DopplerrDb

log = logging.getLogger(__name__)

bp = Blueprint('series', url_prefix="/api/v1/medias/series")


class Media(Model):
    timestamp = DateType()
    type = StringType()
    message = StringType()


class Medias(Model):
    medias = ListType(ModelType(Media))


class Series(Model):
    id = IntType()  # pylint: disable=invalid-name
    tv_db_id = IntType()
    series_title = StringType()


SeriesList = ListType(ModelType(Series))


@describe_add_route(bp, paths="/all", methods="GET")
async def medias_series() -> Medias:
    res = {"medias": DopplerrDb().get_medias_series()}
    return res


@describe_add_route(bp, paths="/", methods="GET")
async def list_series() -> SeriesList:
    return DopplerrDb().list_series()


@describe_add_route(bp, paths="/<id>", methods="GET")
async def get_series(seriesid) -> Series:
    return DopplerrDb().get_series(seriesid)
