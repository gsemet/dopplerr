# coding: utf-8

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
