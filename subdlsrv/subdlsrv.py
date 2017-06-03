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

from klein import Klein
from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import returnValue

from subdlsrv.downloader import Downloader
from subdlsrv.logging import setupLogger

log = logging.getLogger(__name__)
app = Klein()
args = None


def dejsonify(request):
    json_content = request.content.read()
    if json_content:
        content = json.loads(json_content)
    else:
        content = {}
    return content


def jsonify(request, d):
    request.responseHeaders.addRawHeader("content-type", "application/json")
    return json.dumps(d, indent=4, sort_keys=True, separators=(',', ': '))


@app.route("/")
def root():
    return "Status not implemented Yet."


@app.route("/notify", methods=['POST'])
@inlineCallbacks
def notify(request):
    global args
    if args.appdir:
        os.chdir(args.appdir)
    content = dejsonify(request)
    logging.debug("Notify request: %r", content)
    res = yield Downloader(args).process_notify_request(content)
    returnValue(jsonify(request, res))


@app.route("/health")
def health(request):
    healthy = True
    res_health = {"healthy": healthy}
    return jsonify(request, res_health)


@app.route("/fullscan")
@inlineCallbacks
def fullscan(request):
    content = dejsonify(request)
    logging.debug("Fullscan request: %r", content)
    res = yield Downloader(args).process_fullscan(content)
    returnValue(jsonify(request, res))


def inject_env_variables(argv):
    languages = os.environ.get("SUBDLSRC_LANGUAGES")
    if languages:
        argv.append("--languages")
        for l in languages.split(","):
            argv.append(l)
    basedir = os.environ.get("SUBDLSRC_BASEDIR")
    if basedir:
        argv.extend(["--basedir", basedir])


def main():
    argv = sys.argv[1:]
    inject_env_variables(argv)
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', action='store', dest='port', help='The port to listen on')
    parser.add_argument(
        '-b', '--basedir', action='store', dest='basedir', help='Base directory', default="")
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
        choices=["fra", "eng", "ger"],
        required=True)
    global args
    args = parser.parse_args(args=argv)
    setupLogger(level=logging.DEBUG if args.verbose else logging.INFO, no_color=args.no_color)
    log.info("Initializing Subtitle Downloader Service")

    if args.port is None:
        print("Missing required argument: -p/--port")
        sys.exit(1)
    log.debug("Starting listening on port %s", args.port)
    log.debug("Application directory: %s", args.appdir)
    log.debug("Media base directory: %s", args.basedir)
    log.debug("Wanted languages: %s", args.languages)
    if args.path_mapping:
        log.debug("Path Mapping: %r", args.path_mapping)
    Downloader.initialize_subliminal()
    app.run(host='0.0.0.0', port=int(args.port))


if __name__ == '__main__':
    main()
