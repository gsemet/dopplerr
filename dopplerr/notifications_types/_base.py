# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

log = logging.getLogger(__name__)


class _NotificationTypeBase(object):
    pass


class _SeriesNotificationBase(_NotificationTypeBase):
    notification_type = NotImplementedError
    notification_title = NotImplementedError
    series_episode_info = None

    def __init__(self, series_episode_info):
        self.series_episode_info = series_episode_info
