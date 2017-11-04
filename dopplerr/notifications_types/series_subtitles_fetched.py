# coding: utf-8

import logging

from dopplerr.notifications_types._base import _SeriesNotificationBase

log = logging.getLogger(__name__)


# pylint: disable=duplicate-code
class SubtitleFetchedNotification(_SeriesNotificationBase):
    notification_type = "fetched"
    notification_title = "Episode Subtitles Fetched"

    @property
    def one_liner(self):
        return ("{e[series_title]} - {e[season_number]}x{e[episode_number]} - "
                "{e[episode_title]} [{e[quality]}] - Lang: {e[video_languages]} - "
                "Subtitles: {subtitles_languages}".format(
                    e=self.series_episode_info,
                    subtitles_languages=",".join(self.series_episode_info['subtitles_languages']),
                ))
