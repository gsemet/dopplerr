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
from pathlib import PosixPath

from dopplerr.cfgtree import getNodeByPath
from dopplerr.cfgtree import setNodeByPath

log = logging.getLogger(__name__)
_undefined = object()


class _CfgBase(object):

    _DEFAULT = None
    name = None
    xpath = None
    arg_type = None
    environ_var_prefix = None
    ignore_in_cfg = False

    def __init__(self, l=None, s=None, h=None, r=False, d=_undefined):
        # Note: self.name should come later by EnvironmentConfig._inject_names()
        self.short_param = s
        self.help_str = h
        self.required = r
        self.forced_long_param = l
        if d == _undefined:
            self.default = self._DEFAULT
        else:
            self.default = d
        self.value = self.default

    def set_value(self, value):
        """
        Setter method used in setNodeByPath
        """
        self.value = value

    @property
    def environ_var_name(self):
        return self.environ_var_prefix + self.cmd_line_name.upper()

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
        if self.forced_long_param:
            return self.forced_long_param
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


class ConfigFileCfg(StringCfg):
    _DEFAULT = None
    ignore_in_cfg = True


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
                raise argparse.ArgumentTypeError("{!r} not in available choise: {}".format(
                    item, ", ".join(self.choices)))


class EnvironmentConfig(object):
    _CFG = None
    _ENVIRON_VAR_PREFIX = None
    _CONFIGURATION_ENTRY_POINT = None

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
            if self._CFG is None:
                return
            root = self._CFG
        # pylint: disable=no-member
        for name, item in root.items():
            if isinstance(item, dict):
                self._inject_names(root=item, xpath=self.mkxpath(xpath, name))
            else:
                item.name = name
                item.xpath = self.mkxpath(xpath, name)
                item.environ_var_prefix = self._ENVIRON_VAR_PREFIX
                if item.ignore_in_cfg:
                    # log.debug("Create cfg node '%s': ignored (handled later)", item.xpath)
                    continue
                log.debug("Create cfg node: '%s' (name: '%s') with value: %r", item.xpath,
                          item.name, item.safe_value)
        # pylint: enable=no-member

    def set_cfg_value(self, xpath, value):
        """
        Set a value in _CFG
        """
        setNodeByPath(self._CFG, xpath, value, extend=True, setter_attr="set_value")

    def get_cfg_value(self, xpath, default=None):
        """
        Get a value from _CFG
        """
        return getNodeByPath(self._CFG, xpath, default=default).value

    def find_configuration_values(self):
        self._load_configuration()
        self._load_environment_variables("", self._CFG)
        self._load_cmd_line_arg()
        self._save_configuration()

    def _load_configuration(self):
        log.debug("Looking for configuration")
        self._CONFIGURATION_ENTRY_POINT.find_entry_point()
        bare_cfg = self._CONFIGURATION_ENTRY_POINT.get_bare_config_dict()
        self._load_cfg_dict(bare_cfg)

    def _save_configuration(self):
        log.debug("Saving configuration")
        bare_cfg = self._dict(safe=False)
        self._CONFIGURATION_ENTRY_POINT.save_bare_config_dict(bare_cfg)

    def _load_cfg_dict(self, cfg, xpath=None):
        for k, v in cfg.items():
            if isinstance(v, dict):
                self._load_cfg_dict(v, self.mkxpath(xpath, k))
            else:
                self.set_cfg_value(self.mkxpath(xpath, k), v)

    def _load_environment_variables(self, xpath, root):
        """
        Inject value from environment variable
        """
        for name, item in root.items():
            if isinstance(item, dict):
                self._load_environment_variables(self.mkxpath(xpath, name), item)
            else:
                print("item.environ_var_name:", item.environ_var_name)
                if item.environ_var_name in os.environ:
                    if item.ignore_in_cfg:
                        log.debug("Ignoring environment variable %s", item.environ_var_name)
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
            if v is _undefined:
                continue
            cfg.value = v
            if cfg.ignore_in_cfg:
                log.debug("Ignoring command line parameter %s", cfg.long_param)
            log.debug("Found command line parameter '%s': %s (conf: %s)", cfg.long_param,
                      cfg.safe_value, cfg.xpath)
        log.debug("Current configuration: %s", self._json(safe=True))

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
                    "default": _undefined,
                }
                # log.debug("parser arg %s, dest %s", item.long_param, kwargs['dest'])
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

    def _dict(self, root=None, safe=False):
        """
        Return the configuration as a dictionnary
        """
        if root is None:
            root = self._CFG
        d = {}
        # pylint: disable=no-member
        for name, item in root.items():
            if isinstance(item, dict):
                d[name] = self._dict(root=item, safe=safe)
            else:
                if item.ignore_in_cfg:
                    continue
                elif safe:
                    d[name] = item.safe_value
                else:
                    d[name] = item.value
        # pylint: enable=no-member
        return d

    def _json(self, safe=False):
        return json.dumps(self._dict(safe=safe), sort_keys=True, indent=4, separators=(',', ': '))


class _ConfigEntryPointBase(object):
    def find_entry_point(self):
        raise NotImplementedError

    def get_bare_config_dict(self):
        raise NotImplementedError

    def save_bare_config_dict(self, bare_cfg):
        raise NotImplementedError


class JsonFileConfigEntryPoint(_ConfigEntryPointBase):
    _CONFIG_ENTRYPOINY_DEFAULT_FILENAME = None
    _CONFIG_ENTRYPOINT_ENVIRON_VAR_NAME = None
    _CONFIG_ENTRYPOINT_SHORT_PARAM_NAME = None
    _CONFIG_ENTRYPOINT_LONG_PARAM_NAME = None

    _resolved_config_file = None
    _bare_config_dict = None

    def find_entry_point(self):
        configfile = self._CONFIG_ENTRYPOINY_DEFAULT_FILENAME
        if self._CONFIG_ENTRYPOINT_ENVIRON_VAR_NAME in os.environ:
            configfile = os.environ[self._CONFIG_ENTRYPOINT_ENVIRON_VAR_NAME]
            log.debug("%s defined: %s", self._CONFIG_ENTRYPOINT_ENVIRON_VAR_NAME, configfile)
        for i in range(len(sys.argv)):
            good = []
            if self._CONFIG_ENTRYPOINT_SHORT_PARAM_NAME:
                good.append(self._CONFIG_ENTRYPOINT_SHORT_PARAM_NAME)
            if self._CONFIG_ENTRYPOINT_LONG_PARAM_NAME:
                good.append(self._CONFIG_ENTRYPOINT_LONG_PARAM_NAME)
            if sys.argv[i] in good:
                if i == len(sys.argv):
                    raise Exception("No value given to {}".format(" or ".join(good)))
                configfile = sys.argv[i + 1]
                log.debug("%s defined: %s", " or ".join(good), configfile)
                break
        config_file_path = PosixPath(configfile)
        log.info("Configuration file set to: %s", configfile)
        self._resolved_config_file = config_file_path.resolve().as_posix()
        self._load_bare_config()

    def _load_bare_config(self):
        log.debug("(Re)loading configuration file: %s", self._resolved_config_file)
        config_file_path = PosixPath(self._resolved_config_file)
        if config_file_path.exists():
            with config_file_path.open() as f:
                self._bare_config_dict = json.load(f)
        else:
            self._bare_config_dict = {}

    def save_bare_config_dict(self, bare_cfg):
        with PosixPath(self._resolved_config_file).open('w') as f:
            f.write(json.dumps(bare_cfg, sort_keys=True, indent=4, separators=(',', ': ')))

    def get_bare_config_dict(self):
        return self._bare_config_dict
