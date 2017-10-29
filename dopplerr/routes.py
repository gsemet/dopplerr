# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from pathlib import Path

from txwebbackendbase.requests import dejsonify
from txwebbackendbase.requests import jsonify
from txwebbackendbase.singleton import singleton
from txwebbackendbase.threading import deferredAsThread

from klein import Klein
from twisted.internet.defer import inlineCallbacks
from twisted.web.static import File

import dopplerr
from dopplerr.db import DopplerrDb
from dopplerr.downloader import DopplerrDownloader
from dopplerr.request_filter import SonarrFilter
from dopplerr.response import Response
from dopplerr.status import DopplerrStatus

log = logging.getLogger(__name__)


@singleton
class Routes(object):
    app = Klein()
    args = None
    __frontend_static = None
    __frontend_root = None

    def listen(self):
        self.app.run(host='0.0.0.0', port=int(DopplerrStatus().port))

    @property
    def frontend_static(self):
        if self.__frontend_static is None:
            self.__frontend_static = str(Path(DopplerrStatus().frontenddir) / "static")
        return self.__frontend_static

    @property
    def frontend_root(self):
        if self.__frontend_root is None:
            self.__frontend_root = str(Path(DopplerrStatus().frontenddir))
        return self.__frontend_root

    # Double-index method kung-foo
    #   https://github.com/twisted/klein/issues/41
    # pylint: disable=function-redefined
    @app.route("/", branch=True)
    def index(self, _request):
        return File(self.frontend_root)

    @app.route("/", branch=True)
    def index(self, _request):
        return File(self.frontend_root)

    # pylint: enable=function-redefined

    @app.route("/static/", branch=True)
    def static(self, _request):
        return File(self.frontend_static)

    @app.route("/api/v1/events/recent/<num>")
    def recent_events_num(self, request, num=10):
        num = int(num)
        if num > 100:
            num = 100
        res = {"events": DopplerrDb().getLastEvents(num)}
        return jsonify(request, res)

    @app.route("/api/v1/events/recent/")
    def recent_events_10(self, request):
        res = {"events": DopplerrDb().getLastEvents(10)}
        return jsonify(request, res)

    @app.route("/api/v1/notify/sonarr", methods=['POST'])
    @inlineCallbacks
    def notify_sonarr(self, request):
        content = dejsonify(request)
        res = yield self._process_notify_sonarr(content)
        return jsonify(request, res.toDict())

    @deferredAsThread
    def _process_notify_sonarr(self, content):
        logging.debug("Notify sonarr request: %r", content)
        log.debug("Processing request: %r", content)
        res = Response()
        SonarrFilter().filter(content, res)
        if res.is_unhandled:
            # event has been filtered out
            return res
        candidates = res.candidates
        if not candidates:
            DopplerrDb().insertEvent("error", "event handled but no candidate found")
            log.debug("event handled but no candidate found")
            res.update_status("failed", "event handled but no candidate found")
            return res
        for candidate in candidates:
            log.info(
                "Searching episode '%s' from series '%s'. Filename: %s",
                candidate.get("episode_title"),
                candidate.get("series_title"),
                candidate.get("scenename"),
            )
            DopplerrDb().insertEvent("availability notification", "{} - {}x{} - {} [{}] available."
                                     .format(
                                         candidate.get("series_title"),
                                         candidate.get("season_number"),
                                         candidate.get("episode_number"),
                                         candidate.get("episode_title"),
                                         candidate.get("quality"),
                                     ))
            video_files_found = DopplerrDownloader().search_file(candidate['root_dir'],
                                                                 candidate['scenename'])
            log.debug("All found files: %r", video_files_found)
            if not video_files_found:
                res.update_status("failed", "candidates found but no video file found")
            else:
                DopplerrDownloader().download_missing_subtitles(res, video_files_found)
            subtitles = res.subtitles
            if not subtitles:
                DopplerrDb().insertEvent("subtitles", "not subtitles found for: {}"
                                         .format([Path(f).name for f in video_files_found]))
            else:
                DopplerrDb().insertEvent("subtitles", "subtitles fetched: {}".format(
                    ", ".join([
                        "{} (lang: {}, source: {})".format(
                            s.get("filename"),
                            s.get("language"),
                            s.get("provider"),
                        ) for s in subtitles
                    ])))

        return res

    @app.route("/api/v1/notify", methods=['GET'])
    def notify_not_allowed(self, request):
        request.setResponseCode(405)
        return "Method GET not allowed. Use POST with a JSON body with the right format"

    @app.route("/api/v1/health")
    def health(self, request):
        res_health = {
            "healthy": DopplerrStatus().healthy,
            "languages": DopplerrStatus().languages,
            "mapping": DopplerrStatus().path_mapping,
            "version": dopplerr.version,
        }
        return jsonify(request, res_health)

    @app.route("/api/v1/version")
    def version(self, _request):
        return dopplerr.version

    @app.route("/api/v1/fullscan")
    @inlineCallbacks
    def fullscan(self, request):
        content = dejsonify(request)
        logging.debug("Fullscan request: %r", content)
        res = yield DopplerrDownloader().process_fullscan(content)
        return jsonify(request, res)
