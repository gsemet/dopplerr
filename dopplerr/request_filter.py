# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from dopplerr.status import DopplerrStatus

log = logging.getLogger(__name__)


class _FilterBase(object):
    def appy_path_mapping(self, folder):
        if not DopplerrStatus().path_mapping:
            return folder
        if folder.startswith("/"):
            absolute = True
            folder = folder[1:]
        for mapping in DopplerrStatus().path_mapping:
            log.debug("Mapping: %s", mapping)
            k, _, v = mapping.partition("=")
            log.debug("Applying mapping %s => %s", k, v)
            if folder.startswith(k):
                folder = v + folder[len(k):]
                break
        if absolute:
            return "/" + folder
        return folder

    @staticmethod
    def lowerize_dick_keys(thedict):
        return {k.lower(): v for k, v in thedict.items()}


class SonarrFilter(_FilterBase):
    def filter(self, request, res):
        # probably Sonarr
        low_request = self.lowerize_dick_keys(request)
        eventtype = low_request.get("eventtype")
        if eventtype == "Download":
            return self.process_download(request, res)
        return res.unhandled("Ignoring Sonarr event type: {!r}".format(eventtype))

    def process_download(self, request, res):
        log.debug("Processing Sonarr's 'on downloaded' event")
        res.update_status("processing")
        res.set("request_type", "sonarr")
        res.set("request_event", "on download")
        low_request = self.lowerize_dick_keys(request)
        low_series = self.lowerize_dick_keys(low_request.get("series", {}))
        root_dir = low_series.get("path")
        series_title = low_series.get("title")
        if not root_dir:
            return res.failed("Empty Series Path")
        root_dir = self.appy_path_mapping(root_dir)
        log.debug("Root folder: %s", root_dir)
        log.debug("Reconstructing full media path with basedir '%s'", DopplerrStatus().basedir)

        def concat_path(a, b):
            if not a.endswith('/'):
                a += '/'
            if b.startswith('/'):
                b = b[1:]
            a += b
            return a

        root_dir = concat_path(DopplerrStatus().basedir, root_dir)
        basename = root_dir
        log.info("Searching episodes for serie '%s' in '%s'", series_title, root_dir)
        res.update_status("listing candidates")
        for episode in low_request.get("episodes", []):
            low_episode = self.lowerize_dick_keys(episode)
            basename = low_episode.get("scenename", "")
            episode_title = low_episode.get("title", "")
            season_number = low_episode.get("seasonnumber", "")
            episode_number = low_episode.get("episodenumber", "")
            quality = low_episode.get("quality", "")
            log.debug("Candidate: episode '%s' with base filename '%s'", episode_title, basename)
            res.setdefault("candidates", []).append({
                "series_title": series_title,
                "episode_title": episode_title,
                "root_dir": root_dir,
                "scenename": basename,
                "season_number": season_number,
                "episode_number": episode_number,
                "quality": quality,
            })
        res.update_status("candidates listed")
        return res


class AutoDetectFilter(_FilterBase):
    def filter(self, request, res):
        low_request = self.lowerize_dick_keys(request)
        if "series" in low_request:
            return SonarrFilter().filter(request, res)
        return res.failed("Unable to find request type")
