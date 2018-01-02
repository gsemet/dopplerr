# coding: utf-8

# Standard Libraries
import logging
import os
from pathlib import PosixPath

# Third Party Libraries
import pkg_resources
from cfgtree import ConfigBaseModel
from cfgtree.cmdline_parsers.argparse import ArgparseCmdlineParser
from cfgtree.storages.json import JsonFileConfigStorage
from cfgtree.types import BoolCfg
from cfgtree.types import ConfigFileCfg
from cfgtree.types import DirNameCfg
from cfgtree.types import HardcodedCfg
from cfgtree.types import IntCfg
from cfgtree.types import ListOfStringCfg
from cfgtree.types import MultiChoiceCfg
from cfgtree.types import PasswordCfg
from cfgtree.types import SingleChoiceCfg
from cfgtree.types import StringCfg

# Dopplerr
from dopplerr.singleton import singleton

log = logging.getLogger(__name__)
DEFAULT_PORT = 8086


def _find_frontend_data():
    installed_data_frontend = pkg_resources.resource_filename(__name__, 'frontend')
    if PosixPath(installed_data_frontend).exists():
        log.debug("Found local frontend path: %s", installed_data_frontend)
        return installed_data_frontend
    setup_py = pkg_resources.resource_filename(__name__, "main.py")
    dev_env_frontend_dist = PosixPath(setup_py).parent.parent / "frontend" / "dist"
    if dev_env_frontend_dist.exists():
        log.debug("Found dev local frontend path: %s", dev_env_frontend_dist)
        return str(dev_env_frontend_dist)
    return None


@singleton
class DopplerrConfig(ConfigBaseModel):

    environ_var_prefix = "DOPPLERR_"

    storage = JsonFileConfigStorage(
        environ_var="DOPPLERR_COMMON_CONFIG_FILE",
        long_param="--config-file",
        short_param="-g",
        default_filename="config.json",
    )

    cmd_line_parser = ArgparseCmdlineParser()

    # yapf: disable
    model = {
        "configfile": ConfigFileCfg(
            long_param="--config-file",
            summary="Config directory"),
        "debug_config": BoolCfg(
            long_param="--debug-config",
            summary="Show logs before configuration load"),
        "general": {
            "basedir": DirNameCfg(
                short_param="-b",
                default=os.getcwd(),
                summary='Base directory'),
            "configdir": DirNameCfg(
                short_param="-c",
                default=os.getcwd(),
                summary="Config directory"),
            "frontenddir": DirNameCfg(
                short_param="-f",
                default=_find_frontend_data(),
                required=True,
                summary="Frontend directory"),
            "verbose": BoolCfg(
                short_param='-v',
                long_param="--verbose",
                summary='Enable verbose output logs'),
            "output_type": SingleChoiceCfg(
                long_param="--output-type",
                summary="Output log type",
                choices=["quiet", "plain", "dev"],
                default="plain"),
            "logfile": StringCfg(
                short_param="-l",
                summary='Output log to file'),
            "mapping": ListOfStringCfg(
                short_param='-m',
                summary=(
                    "Map root folder of tv/anime/movie to another name.\n"
                    "Ex: series are mounted on a docker image as /tv but \n"
                    "on the other system it is under /video/Series. In this \n"
                    "case use '--basedir /video --mapping tv=Series,movieshort_param=Movies'\n"
                    "Please enter trivial mapping as well:\n"
                    "   '--mapping tv=tv,movieshort_param=movies'"
                )),
            "port": IntCfg(short_param='-p', default=DEFAULT_PORT, summary='The port to listen on'),
            "no_color": BoolCfg(summary="Disable color in logs"),
            "version": HardcodedCfg(),
        },
        "subliminal": {
            "languages": ListOfStringCfg(),
            "addic7ed": {
                "enabled": BoolCfg(summary="Enable addic7ed"),
                "user": StringCfg(summary="addic7ed username"),
                "password": PasswordCfg(summary="addic7ed password"),
            },
            "legendastv": {
                "enabled": BoolCfg(summary="Enable legendastv"),
                "user": StringCfg(summary="legendastv username"),
                "password": PasswordCfg(summary="legendastv password"),
            },
            "opensubtitles": {
                "enabled": BoolCfg(summary="Enable opensubtitles"),
                "user": StringCfg(summary="opensubtitles username"),
                "password": PasswordCfg(summary="opensubtitles password"),
            },
            "subscenter": {
                "enabled": BoolCfg(summary="Enable subscenter"),
                "user": StringCfg(summary="subscenter username"),
                "password": PasswordCfg(summary="subscenter password"),
            },
        },
        "notifications": {
            "pushover": {
                "enabled": BoolCfg(summary="Enable pushover"),
                "user": StringCfg(summary="pushover username"),
                "token": PasswordCfg(summary="pushover password"),
                "registered_notifications": MultiChoiceCfg(
                    summary="Notifications",
                    choices=["fetched"], default=["fetched"]),
            }
        },
        "scanner": {
            "enable": BoolCfg(summary="Enable periodic disc scanner", default=False),
            "interval_hours": IntCfg(summary="Refresh interval (in hours)", default=6),
        }
    }
    # yapf: enable
