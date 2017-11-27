# coding: utf-8

# Standard Libraries
import logging

# Third Party Libraries
from sanic import Blueprint
from schematics.models import Model
from schematics.types import ModelType
from schematics.types import StringType
from schematics.types import URLType

# Dopplerr
from dopplerr.api.add_route import describe_add_route
from dopplerr.config import DopplerrConfig

log = logging.getLogger(__name__)


class Links(Model):
    _self = URLType()


class ConfigDir(Model):
    configdir = StringType(required=True, metadata={"label": "dldl", "description": "descript"})
    basedir = StringType(required=True)
    frontenddir = StringType(required=True)
    _links = ModelType(Links)


bp = Blueprint('config', url_prefix="/api/v1")


@describe_add_route(bp, paths="/config/general/dirs")
async def config_directories(request) -> ConfigDir:
    """
    Get all configuration directories.
    """
    return {
        "configdir": DopplerrConfig().get_cfg_value("general.configdir"),
        "basedir": DopplerrConfig().get_cfg_value("general.basedir"),
        "frontenddir": DopplerrConfig().get_cfg_value("general.frontenddir"),
        "_links": {
            "_self": request.app.url_for("config.config_directories")
        }
    }
