# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import os
import sys

from flask import Flask
from flask import jsonify
from flask import request

from subdlsrv.downloader import Downloader
from subdlsrv.logging import setupLogger

log = logging.getLogger(__name__)
app = Flask(__name__)
args = None


@app.route("/")
def root():
    return "OK"


@app.route("/notify", methods=['POST'])
def notify():
    global args
    if args.appdir:
        os.chdir(args.appdir)

    content = request.json
    logging.debug("Request: %r", content)
    res = Downloader(args).process_notify_request(content)
    return jsonify(res)


@app.route("/health")
def health():
    healthy = True
    res_health = {"healthy": healthy}
    return jsonify(res_health)


@app.route("/fullscan")
def fullscan():
    content = request.json
    logging.debug("Request: %r", content)
    res = Downloader(args).process_fullscan(content)
    return jsonify(res)


def main():
    parser = argparse.ArgumentParser(usage="python simpleapp.py -p ")
    parser.add_argument('-p', '--port', action='store', dest='port', help='The port to listen on')
    parser.add_argument(
        '-b',
        '--basedir',
        action='store',
        dest='basedir',
        help='Base directory',
        default=os.environ.get("SUBDLSRC_BASEDIR", "/"))
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
    global args
    args = parser.parse_args()
    setupLogger(level=logging.DEBUG if args.verbose else logging.INFO, no_color=args.no_color)
    log.info("Initializing Subtitle Downloader Service")

    if args.port is None:
        print("Missing required argument: -p/--port")
        sys.exit(1)
    log.debug("Starting listening on port %s", args.port)
    log.debug("Application directory: %s", args.appdir)
    log.debug("Media base directory: %s", args.basedir)
    app.run(host='0.0.0.0', port=int(args.port), debug=False)


if __name__ == '__main__':
    main()
