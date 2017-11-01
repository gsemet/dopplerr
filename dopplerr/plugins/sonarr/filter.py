# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from dopplerr.config import DopplerrConfig
from dopplerr.request_filter import _FilterBase

log = logging.getLogger(__name__)


class SonarrFilter(_FilterBase):
    async def filter(self, request, res):
        # probably Sonarr
        low_request = self.lowerize_dick_keys(request)
        eventtype = low_request.get("eventtype")
        if eventtype == "Download":
            await self.process_on_download(request, res)
            return res
        return res.unhandled("Ignoring Sonarr event type: {!r}".format(eventtype))

    async def process_on_download(self, request, res):
        log.debug("Processing Sonarr's 'on downloaded' event")
        res.update_status("processing")
        res.request_type = "sonarr"
        res.request_event = "on download"
        low_request = self.lowerize_dick_keys(request)
        low_series = self.lowerize_dick_keys(low_request.get("series", {}))
        root_dir = low_series.get("path")
        series_title = low_series.get("title")
        tv_db_id = low_series.get("tvdbid")
        if not root_dir:
            return res.failed("Empty Series Path")
        root_dir = self.appy_path_mapping(root_dir)
        log.debug("Root folder: %s", root_dir)
        log.debug("Reconstructing full media path with basedir '%s'",
                  DopplerrConfig().get_cfg_value("general.basedir"))

        def concat_path(str_a, str_b):
            if not str_a.endswith('/'):
                str_a += '/'
            if str_b.startswith('/'):
                str_b = str_b[1:]
            str_a += str_b
            return str_a

        root_dir = concat_path(DopplerrConfig().get_cfg_value("general.basedir"), root_dir)
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
            res.candidates.append({
                "series_title": series_title,
                "tv_db_id": tv_db_id,
                "episode_title": episode_title,
                "root_dir": root_dir,
                "scenename": basename,
                "season_number": season_number,
                "episode_number": episode_number,
                "quality": quality,
            })
        res.update_status("candidates listed")
