# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from dopplerr.singleton import singleton

from dopplerr.config import DopplerrConfig

log = logging.getLogger(__name__)


@singleton
class DopplerrStatus(object):
    """
    Contains current status of the application and derived values from DopplerrConfig
    """

    def __init__(self):
        self.healthy = False
        self.sqlite_db_path = None
        self.subliminal_provider_configs = None

    def refresh_from_cfg(self):
        """
        Refresh derived values from cfg
        """
        cfg = DopplerrConfig()
        if not cfg.get_cfg_value("general.port"):
            log.fatal("No port defined !")
            raise Exception("No port defined")
        if not cfg.get_cfg_value("general.frontenddir"):
            log.fatal("No frontend dir defined")
            raise Exception("No frontend dir defined")
        self.subliminal_provider_configs = self._build_subliminal_provider_cfgs()

        languages = cfg.get_cfg_value("subliminal.languages")
        if not languages:
            raise Exception("No languages defined")
        if any(not x for x in languages):
            raise Exception("Bad languages: {!r}".format(languages))

    def _build_subliminal_provider_cfgs(self):
        cfg = DopplerrConfig()
        provider_configs = {}
        provider_names = [
            "addic7ed",
            "legendastv",
            "opensubtitles",
            "subscenter",
        ]
        for provider_name in provider_names:
            if cfg.get_cfg_value("subliminal.{}.enabled".format(provider_name)):
                provider_configs[provider_name] = {
                    'username': cfg.get_cfg_value("subliminal.{}.user".format(provider_name)),
                    'password': cfg.get_cfg_value("subliminal.{}.password".format(provider_name)),
                }
                log.debug("Using %s username: %s", provider_name,
                          provider_configs[provider_name]['username'])
        return provider_configs
