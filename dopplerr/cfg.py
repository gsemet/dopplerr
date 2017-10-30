# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import json
import logging
import os
import sys
from pathlib import Path

import pkg_resources
from txwebbackendbase.singleton import singleton

from dopplerr.cfgtree import getNodeByPath
from dopplerr.cfgtree import setNodeByPath

log = logging.getLogger(__name__)
_undefined = object()
DEFAULT_PORT = 8086


class _CfgBase(object):

    _DEFAULT = None
    name = None
    xpath = None
    arg_type = None

    def __init__(self, s=None, h=None, r=False, d=_undefined):
        # Note: self.name should come later by DopplerrConfig._inject_names()
        self.short_param = s
        self.help_str = h
        self.required = r
        if d == _undefined:
            self.default = self._DEFAULT
        else:
            self.default = d
        self.value = self.default

    @property
    def environ_var_name(self):
        return "DOPPLERR_" + self.name.upper()

    def get_cmd_line_params(self):
        a = []
        if self.short_param:
            a.append(self.short_param)
        if self.name:
            a.append(self.long_param)
        return a

    @property
    def _environ_var_value(self):
        return os.environ.get(self.environ_var_name, _undefined)

    def read_environ_var(self):
        return str(self._environ_var_value)

    @property
    def long_param(self):
        if not self.xpath:
            return "--" + self.name.lower().replace("_", "-")
        return "--" + self.xpath.replace('.', '-').replace('_', '-')

    @property
    def cmd_line_name(self):
        return self.xpath.lower().replace("-", "_").replace(".", "_")

    @property
    def action(self):
        return 'store'

    @property
    def n_args(self):
        return None

    @property
    def safe_value(self):
        """
        string that can be outputed to logs
        """
        return self.value

    @property
    def cfgfile_value(self):
        """
        value as it should be saved in config file
        """
        return self.value if self.value is not None else ""

    @property
    def metavar(self):
        return self.name.upper()


class StringCfg(_CfgBase):
    _DEFAULT = ""

    def read_environ_var(self):
        return str(self.read_environ_var)


class ListOfStringCfg(_CfgBase):
    """
    Comma separated list of string (1 argument)
    """

    def __init__(self, *args, **kwargs):
        self._DEFAULT = []
        super(ListOfStringCfg, self).__init__(*args, **kwargs)

    def read_environ_var(self):
        ls = self._environ_var_value
        return ls.split(",")

    @property
    def cfgfile_value(self):
        """
        value as it should be saved in config file
        """
        return ",".join(self.value)

    @staticmethod
    def arg_type(string):
        return string.split(",")

class IntCfg(_CfgBase):
    _DEFAULT = 0

    def read_environ_var(self):
        return int(self._environ_var_value)


class UserCfg(StringCfg):
    @property
    def user(self):
        return self.value


class PasswordCfg(StringCfg):
    @property
    def password(self):
        return self.value

    @property
    def safe_value(self):
        """
        Hide password in logs
        """
        return "*" * len(self.value)


class DirNameCfg(StringCfg):
    _DEFAULT = None


class BoolCfg(_CfgBase):
    _DEFAULT = False

    def read_environ_var(self):
        e = os.environ.get(self.environ_var_name)
        return bool(e)

    @property
    def action(self):
        return 'store_true'

    @property
    def metavar(self):
        return None


class MultiChoiceCfg(ListOfStringCfg):
    def __init__(self, choices=None, *args, **kwargs):
        super(MultiChoiceCfg, self).__init__(*args, **kwargs)
        self.choices = choices

    def arg_type(self, string):
        items = string.split(",")
        for item in items:
            if item not in self.choices:
                raise argparse.ArgumentTypeError("{!r} not in available choise: {}"
                                                 .format(item, ", ".join(self.choices)))

def _find_frontend_data():
    installed_data_frontend = pkg_resources.resource_filename(__name__, 'frontend')
    if Path(installed_data_frontend).exists():
        log.debug("Found local frontend path: %s", installed_data_frontend)
        return installed_data_frontend
    setup_py = pkg_resources.resource_filename(__name__, "main.py")
    dev_env_frontend_dist = Path(setup_py).parent.parent / "frontend" / "dist"
    if dev_env_frontend_dist.exists():
        log.debug("Found dev local frontend path: %s", dev_env_frontend_dist)
        return str(dev_env_frontend_dist)
    return None


@singleton
class DopplerrConfig(object):

    _CFG = {
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

    def __init__(self):
        self._inject_names()

    @staticmethod
    def mkxpath(xpath, name):
        return xpath + "." + name if xpath else name

    def _inject_names(self, root=None, xpath=None):
        """
        Inject configuration item name defined in the _CFG dict inside each _Cfg
        """
        if root is None:
            root = self._CFG
        for name, item in root.items():
            if isinstance(item, dict):
                self._inject_names(root=item, xpath=self.mkxpath(xpath, name))
            else:
                item.name = name
                item.xpath = self.mkxpath(xpath, name)
                log.debug("cfg: %s ('%s') = %s", item.xpath, item.name, item.value)

    def set_cfg_value(self, xpath, value):
        """
        Set a value in _CFG
        """
        setNodeByPath(self._CFG, xpath, value, extend=True)

    def get_cfg_value(self, xpath, default=None):
        """
        Get a value from _CFG
        """
        return getNodeByPath(self._CFG, xpath, default=default).value

    def find_configuration_values(self):
        self._load_environment_variables("", self._CFG)
        self._load_cmd_line_arg()

    def _load_environment_variables(self, xpath, root):
        """
        Inject value from environment variable
        """
        for name, item in root.items():
            if isinstance(item, dict):
                self._load_environment_variables(self.mkxpath(xpath, name), item)
            elif item.environ_var_name in os.environ:
                val = item.read_environ_var()
                log.debug("Found environment variable '%s': %s (conf: %s)", item.environ_var_name,
                          val, item.xpath)
                item.value = val

    def _load_cmd_line_arg(self):
        """
        Inject parameters provider by the user in the command line
        """
        argv = sys.argv[1:]

        parser = argparse.ArgumentParser()
        self._inject_cfg_in_parser(parser)
        args = parser.parse_args(args=argv)
        for k, v in vars(args).items():
            cfg = self._find_cfg_for_cmd_line_name(k)
            log.debug("Found command line parameter '%s': %s (conf: %s)", cfg.long_param, v,
                      cfg.xpath)
            cfg.value = v
        log.debug("Current configuration: %s", self._json())

    def _find_cfg_for_cmd_line_name(self, cmd_line_name, root=None):
        if root is None:
            root = self._CFG
        for v in root.values():
            if isinstance(v, dict):
                f = self._find_cfg_for_cmd_line_name(cmd_line_name, root=v)
                if f:
                    return f
            else:
                if v.cmd_line_name == cmd_line_name:
                    return v

    def _inject_cfg_in_parser(self, parser, xpath=None, root=None):
        """
        Configure the argument parser according to _CFG
        """
        if root is None:
            root = self._CFG
        # pylint: disable=no-member
        for name, item in root.items():
            if isinstance(item, dict):
                self._inject_cfg_in_parser(parser, xpath=self.mkxpath(xpath, name), root=item)
            else:
                args = item.get_cmd_line_params()
                kwargs = {
                    "action": item.action,
                    "dest": item.cmd_line_name,
                    "help": item.help_str,
                    "default": item.value,
                }
                log.debug("parser arg %s, dest %s, default: %s",
                          item.long_param, kwargs['dest'], kwargs['default'])
                nargs = item.n_args
                if nargs:
                    kwargs["nargs"] = nargs
                metavar = item.metavar
                if metavar:
                    kwargs["metavar"] = metavar
                if item.arg_type is not None:
                    kwargs["type"] = item.arg_type
                parser.add_argument(*args, **kwargs)
        # pylint: enable=no-member

    def _dict(self, root=None):
        """
        Return the configuration as a dictionnary
        """
        if root is None:
            root = self._CFG
        d = {}
        # pylint: disable=no-member
        for name, item in root.items():
            if isinstance(item, dict):
                d[name] = self._dict(root=item)
            else:
                d[name] = item.value
        # pylint: enable=no-member
        return d

    def _json(self):
        return json.dumps(self._dict(), sort_keys=True, indent=4, separators=(',', ': '))
