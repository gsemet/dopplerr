#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import optparse
import os
import sys
import time
import logging

from flask import Flask


app = Flask(__name__)

start = int(round(time.time()))
args = None


@app.route("/")
def proxy_request():
    global args
    if args.appdir:
        os.chdir(args.appdir)

    return "Hello world from Distelli & Docker!"


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-7s - %(message)s')
    logging.debug("initialized")
    parser = optparse.OptionParser(usage="python simpleapp.py -p ")
    parser.add_option('-p', '--port', action='store', dest='port', help='The port to listen on')
    parser.add_option('-b', '--base', action='store', dest='base', help='Base directory',
    default="/")
    parser.add_option('-t', '--type', action='store', dest='type', help='Sonarr or Radarr ?')
    parser.add_option('-a', '--appdir', action='store', dest='appdir', help='App directory',
                      default="")
    global args
    (args, _) = parser.parse_args()
    if args.port is None:
        print("Missing required argument: -p/--port")
        sys.exit(1)
    logging.debug("Running on port %s", args.port)
    app.run(host='0.0.0.0', port=int(args.port), debug=False)

if __name__ == '__main__':
    main()
