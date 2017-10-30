# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import logging.config
import os
import sys
from pathlib import Path

from babelfish import Language
from txwebbackendbase.logging import setupLogger

from dopplerr import dopplerr_version
from dopplerr.cfg import DopplerrConfig
from dopplerr.db import DopplerrDb
from dopplerr.downloader import DopplerrDownloader
from dopplerr.routes import Routes
from dopplerr.status import DopplerrStatus

log = logging.getLogger(__name__)


def print_list(aList):
    return ",".join(aList)


def list_of_languages(langList):
    langs = [s.lower() for s in langList.split(',')]
    failed = False
    for l in langs:
        try:
            Language(l)
        except ValueError:
            failed = True
            logging.critical("Invalid language: %r", l)
    if failed:
        sys.exit(2)
    return langs


def main():
    setupLogger(level=logging.DEBUG, no_color=True)
    log.debug("Initializing Dopplerr version %s...", dopplerr_version)

    DopplerrConfig().find_configuration_values()

    setupLogger(
        level=(logging.DEBUG
               if DopplerrConfig().get_cfg_value("general.verbose") else logging.WARNING),
        no_color=DopplerrConfig().get_cfg_value("general.no_color"),
        logfile=DopplerrConfig().get_cfg_value("general.logfile"))
    DopplerrStatus().refresh_from_cfg()

    log.info("Initializing Subtitle DopplerrDownloader Service")

    DopplerrDownloader().initialize_subliminal()
    DopplerrStatus().sqlite_db_path = (
        Path(DopplerrConfig().get_cfg_value("general.configdir")) / "sqlite.db")
    log.debug("SQLite DB: %s", DopplerrStatus().sqlite_db_path.as_posix())
    DopplerrDb().init(DopplerrStatus().sqlite_db_path)
    DopplerrDb().createTables()

    # change current work dir for subliminal work files
    os.chdir(DopplerrConfig().get_cfg_value("general.configdir"))

    DopplerrDb().insertEvent("start", "dopplerr started")

    # main event loop (Twisted reactor behind)
    Routes().listen()

    DopplerrDb().insertEvent("stop", "dopplerr stopped")
