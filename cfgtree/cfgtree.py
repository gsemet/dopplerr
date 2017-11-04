# coding: utf-8
"""
Configuration Tree management
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import json
import logging
import os
import sys

from cfgtree.dictxpath import get_node_by_xpath
from cfgtree.dictxpath import set_node_by_xpath

log = logging.getLogger(__name__)
_UNDEFINED = object()


class EnvironmentConfig(object):
    cfgtree = None
    environ_var_prefix = None
    config_storage = None

    def __init__(self):
        self._inject_names()

    @staticmethod
    def mkxpath(xpath, name):
        return xpath + "." + name if xpath else name

    def _inject_names(self, root=None, xpath=None):
        """
        Inject configuration item name defined in the cfgtree dict inside each _Cfg
        """
        if root is None:
            if self.cfgtree is None:
                return
            root = self.cfgtree
        # pylint: disable=no-member
        for name, item in root.items():
            if isinstance(item, dict):
                self._inject_names(root=item, xpath=self.mkxpath(xpath, name))
            else:
                item.name = name
                item.xpath = self.mkxpath(xpath, name)
                item.environ_var_prefix = self.environ_var_prefix
                if item.ignore_in_cfg:
                    # log.debug("Create cfg node '%s': ignored (handled later)", item.xpath)
                    continue
                log.debug("Create cfg node: '%s' (name: '%s', cmd line: '%s'), default  : %r",
                          item.xpath, item.name, item.long_param, item.safe_value)
        # pylint: enable=no-member

    def set_cfg_value(self, xpath, value):
        """
        Set a value in cfgtree
        """
        set_node_by_xpath(self.cfgtree, xpath, value, extend=True, setter_attr="set_value")

    def get_cfg_value(self, xpath, default=None):
        """
        Get a value from cfgtree
        """
        return get_node_by_xpath(self.cfgtree, xpath, default=default).value

    def find_configuration_values(self):
        self._load_configuration()
        self._load_environment_variables("", self.cfgtree)
        self._load_cmd_line_arg()
        self._save_configuration()

    def _load_configuration(self):
        log.debug("Looking for configuration")
        self.config_storage.find_config_storage()
        bare_cfg = self.config_storage.get_bare_config_dict()
        self._load_cfg_dict(bare_cfg)

    def _save_configuration(self):
        log.debug("Saving configuration file")
        bare_cfg = self._dict(safe=False)
        self.config_storage.save_bare_config_dict(bare_cfg)

    def _load_cfg_dict(self, cfg, xpath=None):
        for k, v in cfg.items():
            xp = self.mkxpath(xpath, k)
            if isinstance(v, dict):
                self._load_cfg_dict(v, xp)
            else:
                try:
                    self.set_cfg_value(xp, v)
                except KeyError:
                    log.error("Unable to load value '%s' from configuration file, "
                              "no matching item in configuration tree (invalid '%s')", k, xp)

    def _load_environment_variables(self, xpath, root):
        """
        Inject value from environment variable
        """
        for name, item in root.items():
            if isinstance(item, dict):
                self._load_environment_variables(self.mkxpath(xpath, name), item)
            else:
                if item.environ_var_name in os.environ:
                    if item.ignore_in_cfg:
                        log.debug("Ignoring environment variable %s", item.environ_var_name)
                    val = item.read_environ_var()
                    log.debug("Found environment variable '%s': %s (conf: %s)",
                              item.environ_var_name, val, item.xpath)
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
            if v is _UNDEFINED:
                continue
            cfg.value = v
            if cfg.ignore_in_cfg:
                log.debug("Ignoring command line parameter %s", cfg.long_param)
            log.debug("Found command line parameter '%s': %s (conf: %s)", cfg.long_param,
                      cfg.safe_value, cfg.xpath)
        log.debug("Current configuration: %s", self._json(safe=True))

    def _find_cfg_for_cmd_line_name(self, cmd_line_name, root=None):
        if root is None:
            root = self.cfgtree
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
        Configure the argument parser according to cfgtree
        """
        if root is None:
            root = self.cfgtree
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
                    "default": _UNDEFINED,
                }
                nargs = item.n_args
                dbg_infos = ["arg '{}'".format(item.long_param), "dest '{}'".format(kwargs['dest'])]
                if nargs:
                    kwargs["nargs"] = nargs
                    dbg_infos.append("nargs '{}'".format(str(nargs)))
                metavar = item.metavar
                if metavar:
                    kwargs["metavar"] = metavar
                    dbg_infos.append("metavar '{}'".format(metavar))
                if item.arg_type is not None:
                    kwargs["type"] = item.arg_type
                    dbg_infos.append("type '{}'".format(item.arg_type))
                log.debug("parser %s", ", ".join(dbg_infos))
                parser.add_argument(*args, **kwargs)
        # pylint: enable=no-member

    def _dict(self, root=None, safe=False):
        """
        Return the configuration as a dictionnary
        """
        if root is None:
            root = self.cfgtree
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
