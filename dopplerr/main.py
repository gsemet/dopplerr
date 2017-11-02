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
from dopplerr.logging import setupLogger

from dopplerr import DOPPLERR_VERSION
from dopplerr.config import DopplerrConfig
from dopplerr.db import DopplerrDb
from dopplerr.downloader import DopplerrDownloader
from dopplerr.routes import listen
from dopplerr.status import DopplerrStatus

log = logging.getLogger(__name__)


def print_list(alist):
    return ",".join(alist)


def list_of_languages(lang_list):
    langs = [s.lower() for s in lang_list.split(',')]
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
    if "-v" in sys.argv or "--general-verbose" in sys.argv:
        default_level = logging.DEBUG
    else:
        default_level = logging.INFO
    setupLogger(level=default_level, no_color=True)
    log.debug("Initializing Dopplerr version %s...", DOPPLERR_VERSION)

    DopplerrConfig().find_configuration_values()

    setupLogger(
        level=(logging.DEBUG
               if DopplerrConfig().get_cfg_value("general.verbose") else logging.WARNING),
        no_color=DopplerrConfig().get_cfg_value("general.no_color"),
        logfile=DopplerrConfig().get_cfg_value("general.logfile"))
    log.info("Reset logging format to %s", "verbose"
             if DopplerrConfig().get_cfg_value("general.verbose") else "not verbose")

    log.debug("Applying configuration")
    DopplerrStatus().refresh_from_cfg()

    log.info("Initializing Subtitle DopplerrDownloader Service")

    DopplerrDownloader().initialize_subliminal()
    DopplerrStatus().sqlite_db_path = (
        Path(DopplerrConfig().get_cfg_value("general.configdir")) / "sqlite.db")
    log.debug("SQLite DB: %s", DopplerrStatus().sqlite_db_path.as_posix())
    DopplerrDb().init(DopplerrStatus().sqlite_db_path)
    DopplerrDb().create_tables()

    # change current work dir for subliminal work files
    os.chdir(DopplerrConfig().get_cfg_value("general.configdir"))

    DopplerrDb().insert_event("start", "dopplerr started")

    # main event loop (Asyncio behind)
    listen()

    logging.info("Clean stopping")
    DopplerrDb().insert_event("stop", "dopplerr stopped")
