# coding: utf-8

# Standard Libraries
import logging
import os
import sys
from pathlib import Path

# Dopplerr
from dopplerr import DOPPLERR_VERSION
from dopplerr.config import DopplerrConfig
from dopplerr.db import DopplerrDb
from dopplerr.logging import OutputType
from dopplerr.logging import setup_logging
from dopplerr.routes import listen
from dopplerr.status import DopplerrStatus
from dopplerr.tasks.subtasks.subliminal import SubliminalSubDownloader

log = logging.getLogger(__name__)


def main():
    outputtype = OutputType.PLAIN
    if "--debug-config" in sys.argv:
        default_level = logging.DEBUG
    else:
        default_level = logging.ERROR
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--output-type":
            if i < len(sys.argv) and sys.argv[i + 1] == "dev":
                outputtype = OutputType.DEV
                break

    debug = default_level is logging.DEBUG
    setup_logging(debug=debug, outputtype=outputtype)
    log.debug("Initializing Dopplerr version %s...", DOPPLERR_VERSION)

    DopplerrConfig().find_configuration_values()
    log.debug("Current configuration: %s", DopplerrConfig().json(safe=True))

    debug = DopplerrConfig().get_cfg_value("general.verbose")
    output_type = DopplerrConfig().get_cfg_value("general.output_type")
    if output_type == 'dev':
        outputtype = OutputType.DEV
    elif output_type == 'plain':
        outputtype = OutputType.PLAIN
    else:
        raise NotImplementedError("Invalid output type: {!r}".format(output_type))

    log.debug("Applying configuration")
    custom_log_levels = [
        ("peewee", logging.DEBUG if debug else logging.ERROR),
        ("sanic", logging.INFO),
        ("cfgtree", logging.DEBUG if debug else logging.ERROR),
        ("apscheduler", logging.INFO),
        # Subliminal loggers
        ("chardet", logging.ERROR),
        ("dogpile", logging.ERROR),
        ("enzyme", logging.ERROR),
        ("rebulk.processors", logging.INFO),
        ("rebulk", logging.ERROR),
        ("subliminal.providers", logging.ERROR),
        ("subliminal.score", logging.ERROR),
        ("subliminal.subtitle", logging.ERROR),
        ("subliminal", logging.INFO),
        ("urllib3", logging.ERROR),
    ]
    setup_logging(
        outputtype=outputtype,
        debug=debug,
        logfile=DopplerrConfig().get_cfg_value("general.logfile"),
        custom_log_levels=custom_log_levels)
    log.info("Logging is set to %s", "verbose"
             if DopplerrConfig().get_cfg_value("general.verbose") else "not verbose")
    DopplerrStatus().refresh_from_cfg()
    # Backup configuration, now refresh_from_cfg has updated the version
    DopplerrConfig().save_configuration()

    log.info("Initializing Subtitle DopplerrDownloader Service")

    SubliminalSubDownloader.initialize_db()
    DopplerrStatus().sqlite_db_path = (
        Path(DopplerrConfig().get_cfg_value("general.configdir")) / "sqlite.db")
    reset_db = False
    if DopplerrStatus().has_minor_version_changed:
        log.warning("Major version change, dropping all databases")
        reset_db = True
    else:
        log.info("Previous version was %s, now: %s",
                 DopplerrStatus().previous_version,
                 DopplerrConfig().get_cfg_value("general.version"))
    log.debug("SQLite DB: %s", DopplerrStatus().sqlite_db_path.as_posix())
    DopplerrDb().init(DopplerrStatus().sqlite_db_path, reset_db=reset_db)
    DopplerrDb().create_tables()

    # change current work dir for subliminal work files
    os.chdir(DopplerrConfig().get_cfg_value("general.configdir"))

    DopplerrDb().insert_event("start", "dopplerr started")

    # main event loop (Asyncio behind)
    listen()

    logging.info("Clean stopping")
    DopplerrDb().insert_event("stop", "dopplerr stopped")

    return 0
