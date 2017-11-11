# coding: utf-8

import logging

from sanic import Blueprint
from sanic_transmute import add_route
from sanic_transmute import describe
from schematics.models import Model
from schematics.types import StringType

from dopplerr.config import DopplerrConfig

log = logging.getLogger(__name__)


class ConfigDir(Model):
    configdir = StringType()
    basedir = StringType()
    frontenddir = StringType()


bp = Blueprint('config', url_prefix="/api/v1")


@describe(paths="/config/general/dirs")
async def config_directories() -> ConfigDir:
    return {
        "configdir": DopplerrConfig().get_cfg_value("general.configdir"),
        "basedir": DopplerrConfig().get_cfg_value("general.basedir"),
        "frontenddir": DopplerrConfig().get_cfg_value("general.frontenddir"),
    }


add_route(bp, config_directories)
