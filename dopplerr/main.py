# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import os
import sys

from pathlib import Path

import pkg_resources

from txwebbackendbase.logging import setupLogger

from dopplerr.db import DopplerrDb
from dopplerr.downloader import DopplerrDownloader
from dopplerr.routes import Routes
from dopplerr.status import DopplerrStatus

log = logging.getLogger(__name__)
ALLOWED_LANGUAGES = ["fra", "eng", "ger"]


def print_list(aList):
    return ",".join(aList)


def list_of_languages(langList):
    langs = [s.lower() for s in langList.split(',')]
    failed = False
    for l in langs:
        if l not in ALLOWED_LANGUAGES:
            failed = True
            logging.fatal("Invalid language: %r")
    if failed:
        logging.fatal("List of allowed languages: %s", print_list(ALLOWED_LANGUAGES))
        raise argparse.ArgumentTypeError("Invalid language")
    return langs


def inject_env_variables(argv):
    languages = os.environ.get("DOPPLERR_LANGUAGES")
    if languages:
        argv.extend(["--languages", languages])
    basedir = os.environ.get("DOPPLERR_BASEDIR")
    if basedir:
        argv.extend(["--basedir", basedir])
    verbose = os.environ.get("DOPPLERR_VERBOSE")
    if str(verbose).strip() == "1":
        argv.extend(["--verbose"])
    logfile = os.environ.get("DOPPLERR_LOGFILE")
    if logfile:
        argv.extend(["--logfile", logfile])
    mapping = os.environ.get("DOPPLERR_MAPPING")
    if mapping:
        argv.extend(["--mapping", mapping])
    port = os.environ.get("DOPPLERR_PORT")
    if port:
        argv.extend(["--port", port])
    addic7ed = os.environ.get("DOPPLERR_ADDIC7ED_USERNAME")
    if addic7ed:
        argv.extend(["--addic7ed", addic7ed, os.environ.get("DOPPLERR_ADDIC7ED_PASSWORD")])
    legendastv = os.environ.get("DOPPLERR_LEGENDASTV_USERNAME")
    if legendastv:
        argv.extend(["--legendastv", legendastv, os.environ.get("DOPPLERR_LEGENDASTV_PASSWORD")])
    opensubtitles = os.environ.get("DOPPLERR_OPENSUBTITLES_USERNAME")
    if opensubtitles:
        argv.extend(
            ["--opensubtitles", opensubtitles,
             os.environ.get("DOPPLERR_OPENSUBTITLES_PASSWORD")])
    subscenter = os.environ.get("DOPPLERR_SUBSCENTER_USERNAME")
    if subscenter:
        argv.extend(["--subscenter", subscenter, os.environ.get("DOPPLERR_SUBSCENTER_PASSWORD")])


def parse_subliminal_args(args):
    provider_configs = {}
    if args.creds_addic7ed:
        provider_configs['addic7ed'] = {
            'username': args.creds_addic7ed[0],
            'password': args.creds_addic7ed[1],
        }
        log.debug("Using addic7ed username: %s", provider_configs['addic7ed']['username'])
    if args.creds_legendastv:
        provider_configs['legendastv'] = {
            'username': args.creds_legendastv[0],
            'password': args.creds_legendastv[1],
        }
        log.debug("Using legendastv username: %s", provider_configs['legendastv']['username'])
    if args.creds_opensubtitles:
        provider_configs['opensubtitles'] = {
            'username': args.creds_opensubtitles[0],
            'password': args.creds_opensubtitles[1],
        }
        log.debug("Using opensubtitles username: %s", provider_configs['opensubtitles']['username'])
    if args.creds_subscenter:
        provider_configs['subscenter'] = {
            'username': args.creds_subscenter[0],
            'password': args.creds_subscenter[1],
        }
        log.debug("Using subscenter username: %s", provider_configs['subscenter']['username'])
    return provider_configs


def find_frontend_data():
    installed_data_frontend = pkg_resources.resource_filename(__name__, 'frontend')
    if Path(installed_data_frontend).exists():
        return installed_data_frontend
    setup_py = pkg_resources.resource_filename(__name__, "main.py")
    dev_env_frontend_dist = Path(setup_py).parent.parent / "frontend" / "dist"
    if dev_env_frontend_dist.exists():
        return str(dev_env_frontend_dist)

def define_parameters(parser):
    parser.add_argument('-p', '--port', action='store', dest='port', help='The port to listen on')
    parser.add_argument(
        '-b', '--basedir', action='store', dest='basedir', help='Base directory', default="")
    parser.add_argument(
        '-c', '--configdir', action='store', dest='configdir', help='Config directory')
    parser.add_argument(
        '-a', '--appdir', action='store', dest='appdir', help='App directory', default="")
    parser.add_argument(
        '--frontend', action='store', dest='frontenddir', help='Frontend directory',
        default=None)
    parser.add_argument(
        '-n',
        '--no-color',
        action='store_true',
        dest='no_color',
        help='Disable color in logs',
        default=False)
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        dest='verbose',
        help='Verbose output',
        default=False)
    parser.add_argument(
        '--mapping',
        action="store",
        dest="path_mapping",
        nargs="*",
        help=("Map root folder of tv/anime/movie to another name.\n"
              "Ex: series are mounted on a docker image as /tv but \n"
              "on the other system it is under /video/Series. In this \n"
              "case use '--basedir /video --mapping tv=Series movies=Movies'"))
    parser.add_argument(
        "-l",
        "--languages",
        action="store",
        dest="languages",
        help="Wanted languages (comma separated list)",
        type=list_of_languages)
    parser.add_argument(
        "--logfile",
        action="store",
        dest="logfile",
        help="Output log to file",
    )
    parser.add_argument(
        "--addic7ed",
        action="store",
        dest="creds_addic7ed",
        nargs=2,
        required=False,
        help="addic7ed credential (--addic7ed USERNAME PASSWORD)",
    )
    parser.add_argument(
        "--legendastv",
        action="store",
        dest="creds_legendastv",
        nargs=2,
        required=False,
        help="legendastv credential (--legendastv USERNAME PASSWORD)",
    )
    parser.add_argument(
        "--opensubtitles",
        action="store",
        dest="creds_opensubtitles",
        nargs=2,
        required=False,
        help="opensubtitles credential (--opensubtitles USERNAME PASSWORD)",
    )
    parser.add_argument(
        "--subscenter",
        action="store",
        dest="creds_subscenter",
        nargs=2,
        required=False,
        help="subscenter credential (--subscenter USERNAME PASSWORD)",
    )


def setup_status(args):
    if args.port is None:
        log.fatal("Missing required argument: -p/--port")
        sys.exit(1)
    if not args.appdir:
        log.info("No appdir defined, using current folder")
        args.appdir = os.getcwd()
    if not args.basedir:
        log.info("No basedir defined, using current folder")
        args.basedir = os.getcwd()
    if not args.configdir:
        log.info("No configdir defined, using current folder")
        args.configdir = os.getcwd()
    if not args.frontenddir:
        args.frontenddir = find_frontend_data()
    if not args.frontenddir:
        log.fatal("No frontend dir defined")
        raise Exception("No frontend dir defined")
    DopplerrStatus().healthy = True
    DopplerrStatus().appdir = args.appdir
    DopplerrStatus().port = args.port
    DopplerrStatus().path_mapping = args.path_mapping
    DopplerrStatus().configdir = args.configdir
    DopplerrStatus().basedir = args.basedir
    DopplerrStatus().languages = args.languages
    DopplerrStatus().frontenddir = str(Path(args.frontenddir).absolute())
    DopplerrStatus().subliminal_provider_configs = parse_subliminal_args(args)

    log.debug("Starting listening on port %s", DopplerrStatus().port)
    assert DopplerrStatus().port, "port should be defined"
    log.debug("Application directory: %s", DopplerrStatus().appdir)
    assert DopplerrStatus().appdir, "appdir not defined"
    log.debug("Media base directory: %s", DopplerrStatus().basedir)
    assert DopplerrStatus().basedir, "basedir not defined"
    log.debug("Config directory: %s", DopplerrStatus().configdir)
    log.debug("Frontend directory: %s", DopplerrStatus().frontenddir)
    assert DopplerrStatus().configdir, "configdir not defined"
    log.debug("Wanted languages: %s", DopplerrStatus().languages)
    if not DopplerrStatus().languages or any(not x for x in DopplerrStatus().languages):
        raise Exception("Bad languages: {!r}".format(DopplerrStatus().languages))
    if DopplerrStatus().path_mapping:
        log.debug("Path Mapping: %r", DopplerrStatus().path_mapping)
    else:
        log.debug("No path mapping defined")


def main():
    argv = sys.argv[1:]
    inject_env_variables(argv)

    parser = argparse.ArgumentParser()
    define_parameters(parser)
    args = parser.parse_args(args=argv)

    setupLogger(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        no_color=args.no_color,
        logfile=args.logfile)
    log.info("Initializing Subtitle DopplerrDownloader Service")

    setup_status(args)

    DopplerrDownloader().initialize_subliminal()
    DopplerrStatus().sqlite_db_path = Path(args.configdir) / "sqlite.db"
    log.debug("SQLite DB: %s", DopplerrStatus().sqlite_db_path.as_posix())
    DopplerrDb().init(DopplerrStatus().sqlite_db_path)
    DopplerrDb().createTables()

    # change current work dir for subliminal work files
    os.chdir(DopplerrStatus().configdir)

    DopplerrDb().insertEvent("start", "dopplerr started")

    # main event loop (Twisted reactor behind)
    Routes().listen()

    DopplerrDb().insertEvent("stop", "dopplerr stopped")


if __name__ == '__main__':
    main()
