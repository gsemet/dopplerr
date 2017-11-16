# coding: utf-8

import logging

log = logging.getLogger(__name__)


class _NotificationTypeBase(object):
    pass


class _SeriesNotificationBase(_NotificationTypeBase):
    notification_type: str = None
    notification_title: str = None
    series_episode_info = None

    def __init__(self, series_episode_info):
        self.series_episode_info = series_episode_info
