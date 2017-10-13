# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import logging
import os

from klein import Klein
from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import returnValue

from dopplerr.downloader import Downloader


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
def root(_request):
    return "Status page not implemented Yet."


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


@app.route("/notify", methods=['GET'])
def notify_not_allowed(request):
    request.setResponseCode(405)
    return "Method GET not allowed. Use POST with a JSON body with the right format"


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
