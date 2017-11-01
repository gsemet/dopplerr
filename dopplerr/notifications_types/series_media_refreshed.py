# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from dopplerr.notifications_types._base import _SeriesNotificationBase

log = logging.getLogger(__name__)


class SeriesMediaRefreshedNotification(_SeriesNotificationBase):
    notification_type = "refresh"
    notification_title = "Episode Information Refreshed"

    @property
    def one_liner(self):
        return ("{e.series_title} - {e.season_number}x{e.episode_number} - "
                "{e.episode_title} [{e.quality}] - Lang: {video_languages}".format(
                    e=self.series_episode_info,
                    video_languages=",".join(self.series_episode_info.video_languages),
                ))
