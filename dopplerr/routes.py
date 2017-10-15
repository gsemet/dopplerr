# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os

from txwebbackendbase.requests import dejsonify
from txwebbackendbase.requests import jsonify

from klein import Klein
from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import returnValue

from txwebbackendbase.singleton import singleton

from dopplerr.downloader import Downloader
from dopplerr.status import DopplerrStatus


log = logging.getLogger(__name__)


@singleton
class Routes(object):
    app = Klein()
    args = None

    def listen(self):
        self.app.run(host='0.0.0.0', port=int(DopplerrStatus().port))

    @app.route("/")
    def root(self, _request):
        return ("Status page not implemented Yet. <br>"
                "Use /health for health information <br><br>")

    @app.route("/notify", methods=['POST'])
    @inlineCallbacks
    def notify(self, request):
        if DopplerrStatus().appdir:
            os.chdir(DopplerrStatus().appdir)
        content = dejsonify(request)
        logging.debug("Notify request: %r", content)
        res = yield Downloader().process_notify_request(content)
        returnValue(jsonify(request, res))

    @app.route("/notify", methods=['GET'])
    def notify_not_allowed(self, request):
        request.setResponseCode(405)
        return "Method GET not allowed. Use POST with a JSON body with the right format"

    @app.route("/health")
    def health(self, request):
        res_health = {
            "healthy": DopplerrStatus().healthy,
            "languages": DopplerrStatus().languages,
            "mapping": DopplerrStatus().path_mapping,
        }
        return jsonify(request, res_health)

    @app.route("/fullscan")
    @inlineCallbacks
    def fullscan(self, request):
        content = dejsonify(request)
        logging.debug("Fullscan request: %r", content)
        res = yield Downloader().process_fullscan(content)
        returnValue(jsonify(request, res))
