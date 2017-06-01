#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import os
import sys

import devpy

from flask import Flask

app = Flask(__name__)
args = None


@app.route("/")
def proxy_request():
    global args
    if args.appdir:
        os.chdir(args.appdir)

    return "Hello world from Distelli & Docker!"


def main():
    log = devpy.dev_mode()
    log.info("Initializing Subtitle Downloader Service")
    parser = argparse.ArgumentParser(usage="python simpleapp.py -p ")
    parser.add_argument('-p', '--port', action='store', dest='port', help='The port to listen on')
    parser.add_argument('-b', '--base', action='store', dest='base', help='Base directory',
                        default=os.environ.get("SUBDLSRC_BASE", "/"))
    parser.add_argument('-t', '--type', action='store', dest='type', help='Sonarr or Radarr ?')
    parser.add_argument('-a', '--appdir', action='store', dest='appdir', help='App directory',
                        default="")
    global args
    args = parser.parse_args()

    if args.port is None:
        print("Missing required argument: -p/--port")
        sys.exit(1)
    log.info("Running on port %s", args.port)
    app.run(host='0.0.0.0', port=int(args.port), debug=False)


if __name__ == '__main__':
    main()
