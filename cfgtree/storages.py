# coding: utf-8

import json
import logging
import os
import sys
from pathlib import PosixPath

log = logging.getLogger(__name__)


class _ConfigStorageBase(object):
    def find_config_storage(self):
        raise NotImplementedError

    def get_bare_config_dict(self):
        raise NotImplementedError

    def save_bare_config_dict(self, bare_cfg):
        raise NotImplementedError


class JsonFileConfigStorage(_ConfigStorageBase):
    json_configstorage_default_filename = None
    json_configstorage_environ_var_name = None
    json_configstorage_short_param_name = None
    json_configstorage_long_param_name = None

    __resolved_config_file = None
    __bare_config_dict = None

    def find_config_storage(self):
        configfile = self.json_configstorage_default_filename
        if self.json_configstorage_environ_var_name in os.environ:
            configfile = os.environ[self.json_configstorage_environ_var_name]
            log.debug("%s defined: %s", self.json_configstorage_environ_var_name, configfile)
        for i in range(len(sys.argv)):
            good = []
            if self.json_configstorage_short_param_name:
                good.append(self.json_configstorage_short_param_name)
            if self.json_configstorage_long_param_name:
                good.append(self.json_configstorage_long_param_name)
            if sys.argv[i] in good:
                if i == len(sys.argv):
                    raise Exception("No value given to {}".format(" or ".join(good)))
                configfile = sys.argv[i + 1]
                log.debug("%s defined: %s", " or ".join(good), configfile)
                break
        config_file_path = PosixPath(configfile)
        log.debug("Configuration file set to: %s", configfile)
        self.__resolved_config_file = config_file_path.resolve().as_posix()
        self._load_bare_config()

    def _load_bare_config(self):
        log.debug("Loading configuration file: %s", self.__resolved_config_file)
        config_file_path = PosixPath(self.__resolved_config_file)
        if config_file_path.exists():
            with config_file_path.open() as f:
                self.__bare_config_dict = json.load(f)
        else:
            self.__bare_config_dict = {}

    def save_bare_config_dict(self, bare_cfg):
        with PosixPath(self.__resolved_config_file).open('w') as f:
            f.write(json.dumps(bare_cfg, sort_keys=True, indent=4, separators=(',', ': ')))

    def get_bare_config_dict(self):
        return self.__bare_config_dict
