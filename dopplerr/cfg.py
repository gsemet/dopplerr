# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os
from pathlib import PosixPath

import pkg_resources
from txwebbackendbase.singleton import singleton

from dopplerr.environment_config import BoolCfg
from dopplerr.environment_config import ConfigFileCfg
from dopplerr.environment_config import DirNameCfg
from dopplerr.environment_config import EnvironmentConfig
from dopplerr.environment_config import IntCfg
from dopplerr.environment_config import JsonFileConfigStorage
from dopplerr.environment_config import ListOfStringCfg
from dopplerr.environment_config import MultiChoiceCfg
from dopplerr.environment_config import PasswordCfg
from dopplerr.environment_config import StringCfg
from dopplerr.environment_config import UserCfg

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


class DopplerrJsonConfigFile(JsonFileConfigStorage):
    json_configstorage_environ_var_name = "DOPPLERR_COMMON_CONFIG_FILE"
    json_configstorage_long_param_name = "--configfile"
    json_configstorage_short_param_name = "-g"
    json_configstorage_default_filename = "config.json"


@singleton
class DopplerrConfig(EnvironmentConfig):

    environ_var_prefix = "DOPPLERR_"
    config_storage = DopplerrJsonConfigFile()

    cfgtree = {
        "configfile": ConfigFileCfg(l="--configfile", h="Config directory"),
        "general": {
            "basedir":
                DirNameCfg(s="-b", d=os.getcwd(), h='Base directory'),
            "configdir":
                DirNameCfg(s="-c", d=os.getcwd(), h="Config directory"),
            "appdir":
                DirNameCfg(s="-a", d=os.getcwd(), h="App directory"),
            "frontenddir":
                DirNameCfg(s="-f", d=_find_frontend_data(), r=True, h="Frontend directory"),
            "verbose":
                BoolCfg(s='-v', h='Enable verbose output'),
            "logfile":
                StringCfg(s="-l", h='Output log to file'),
            "mapping":
                ListOfStringCfg(
                    s='-m',
                    h=("Map root folder of tv/anime/movie to another name.\n"
                       "Ex: series are mounted on a docker image as /tv but \n"
                       "on the other system it is under /video/Series. In this \n"
                       "case use '--basedir /video --mapping tv=Series,movies=Movies'")),
            "port":
                IntCfg(s='-p', d=DEFAULT_PORT, h='The port to listen on'),
            "no_color":
                BoolCfg(h="Disable color in logs"),
        },
        "subliminal": {
            "languages": ListOfStringCfg(),
            "addic7ed": {
                "enabled": BoolCfg(h="Enable addic7ed"),
                "user": UserCfg(h="addic7ed username"),
                "password": PasswordCfg(h="addic7ed password"),
            },
            "legendastv": {
                "enabled": BoolCfg(h="Enable legendastv"),
                "user": UserCfg(h="legendastv username"),
                "password": PasswordCfg(h="legendastv password"),
            },
            "opensubtitles": {
                "enabled": BoolCfg(h="Enable opensubtitles"),
                "user": UserCfg(h="opensubtitles username"),
                "password": PasswordCfg(h="opensubtitles password"),
            },
            "subscenter": {
                "enabled": BoolCfg(h="Enable subscenter"),
                "user": UserCfg(h="subscenter username"),
                "password": PasswordCfg(h="subscenter password"),
            },
        },
        "notifications": {
            "pushover": {
                "enabled":
                    BoolCfg(h="Enable pushover"),
                "user":
                    UserCfg(h="pushover username"),
                "token":
                    PasswordCfg(h="pushover password"),
                "registered_notifications":
                    MultiChoiceCfg(h="Registerd Notifications", choices=["fetched"], d=["fetched"]),
            }
        }
    }
