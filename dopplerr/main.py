# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import os
import sys

from txwebbackendbase.logging import setupLogger

from dopplerr.downloader import Downloader
from dopplerr.routes import app

log = logging.getLogger(__name__)
ALLOWED_LANGUAGES = ["fra", "eng", "ger"]


def printList(aList):
    return ",".join(aList)


def listOfLanguages(langList):
    langs = [s.lower() for s in langList.split(',')]
    failed = False
    for l in langs:
        if l not in ALLOWED_LANGUAGES:
            failed = True
            logging.fatal("Invalid language: %r")
    if failed:
        logging.fatal("List of allowed languages: %s", printList(ALLOWED_LANGUAGES))
        raise argparse.ArgumentTypeError("Invalid language")


def inject_env_variables(argv):
    languages = os.environ.get("SUBDLSRC_LANGUAGES")
    if languages:
        argv.append(["--languages", languages])
    basedir = os.environ.get("SUBDLSRC_BASEDIR")
    if basedir:
        argv.extend(["--basedir", basedir])
    verbose = os.environ.get("SUBDLSRC_VERBOSE")
    if str(verbose).strip() == "1":
        argv.extend(["--verbose"])
    logfile = os.environ.get("SUBDLSRC_LOGFILE")
    if logfile:
        argv.extend(["--logfile", logfile])


def main():
    argv = sys.argv[1:]
    inject_env_variables(argv)
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', action='store', dest='port', help='The port to listen on')
    parser.add_argument(
        '-b', '--basedir', action='store', dest='basedir', help='Base directory', default="")
    parser.add_argument(
        '-c', '--configdir', action='store', dest='configdir', help='Config directory')
    parser.add_argument(
        '-a', '--appdir', action='store', dest='appdir', help='App directory', default="")
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
        nargs="+",
        help="Wanted languages",
        type=listOfLanguages,
        required=True)
    parser.add_argument(
        "--logfile",
        action="store",
        dest="logfile",
        help="Output log to file",
    )

    args = parser.parse_args(args=argv)
    setupLogger(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        no_color=args.no_color,
        logfile=args.logfile)
    log.info("Initializing Subtitle Downloader Service")

    if args.port is None:
        print("Missing required argument: -p/--port")
        sys.exit(1)
    log.debug("Starting listening on port %s", args.port)
    log.debug("Application directory: %s", args.appdir)
    log.debug("Media base directory: %s", args.basedir)
    log.debug("Config directory: %s", args.configdir)
    log.debug("Wanted languages: %s", args.languages)
    if args.path_mapping:
        log.debug("Path Mapping: %r", args.path_mapping)
    Downloader.initialize_subliminal()
    app.run(host='0.0.0.0', port=int(args.port))


if __name__ == '__main__':
    main()
