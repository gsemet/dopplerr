# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import aiohttp

from dopplerr.config import DopplerrConfig

log = logging.getLogger(__name__)


class NotificationBase(object):

    NOTIFICATION_TYPES = ["fetched"]

    def __init__(self, registered_notification):
        self._registered_notification = registered_notification

    def can_emit_notification_type(self, requested_notif_type):
        return requested_notif_type in self._registered_notification


class NotificationPushOver(NotificationBase):

    __api_url = "https://api.pushover.net/1/messages.json"

    def __init__(self, token, user, registered_notifications):
        self.token = token
        self.user = user
        super(NotificationPushOver, self).__init__(registered_notifications)

    async def emit(self, notification_type, title, message):
        if not self.can_emit_notification_type(notification_type):
            log.debug("notification %s is ignored for pushover")
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    "POST",
                    self.__api_url,
                    json={
                        "token": self.token,
                        "user": self.user,
                        "message": message,
                        "title": title,
                    }) as result:
                response = await result.json()
                log.debug("PushOver response: %r", response)


class _NotificationBase(object):
    pass


class SeriesMediaRefreshedNotification(_NotificationBase):
    notification_type = "refresh"
    notification_title = "Episode Information Refreshed"
    series_title = None
    tv_db_id = None
    season_number = None
    episode_number = None
    episode_title = None
    quality = None
    video_languages = None
    dirty = None
    media_filename = None

    def __init__(self, series_title, tv_db_id, season_number, episode_number, episode_title,
                 quality, video_languages, dirty, media_filename):
        self.series_title = series_title
        self.tv_db_id = tv_db_id
        self.season_number = season_number
        self.episode_number = episode_number
        self.episode_title = episode_title
        self.quality = quality
        self.video_languages = video_languages
        self.dirty = dirty
        self.media_filename = media_filename

    @property
    def one_liner(self):
        return ("{series_title} - {season_number}x{episode_number} - "
                "{episode_title} [{quality}] - Lang: {video_languages}".format(
                    series_title=self.series_title,
                    season_number=self.season_number,
                    episode_number=self.episode_number,
                    episode_title=self.episode_number,
                    quality=self.quality,
                    video_languages=self.video_languages,
                ))


class SubtitleFetchedNotification(_NotificationBase):
    notification_type = "fetched"
    notification_title = "Episode Subtitles Fetched"
    series_title = None
    tv_db_id = None
    season_number = None
    episode_number = None
    episode_title = None
    quality = None
    video_languages = None
    subtitles_languages = None

    def __init__(self, series_title, tv_db_id, season_number, episode_number, episode_title,
                 quality, video_languages, subtitles_languages):
        self.series_title = series_title
        self.tv_db_id = tv_db_id
        self.season_number = season_number
        self.episode_number = episode_number
        self.episode_title = episode_title
        self.quality = quality
        self.video_languages = video_languages
        self.subtitles_languages = subtitles_languages

    @property
    def one_liner(self):
        return ("{series_title} - {season_number}x{episode_number} - "
                "{episode_title} [{quality}] - Lang: {video_languages} - "
                "Subtitles: {subtitles_languages}".format(
                    series_title=self.series_title,
                    season_number=self.season_number,
                    episode_number=self.episode_number,
                    episode_title=self.episode_number,
                    quality=self.quality,
                    video_languages=self.video_languages,
                    subtitles_languages=",".join(self.subtitles_languages),
                ))


async def emit_notifications(notification):
    log.debug("Emiting notification: [%s] %s - %s", notification.notification_type,
              notification.notification_title, notification.one_liner)
    if DopplerrConfig().get_cfg_value("notifications.pushover.enabled"):
        log.debug("Emiting pushover with user %s",
                  DopplerrConfig().get_cfg_value("notifications.pushover.user"))
        po = NotificationPushOver(
            DopplerrConfig().get_cfg_value("notifications.pushover.token"),
            DopplerrConfig().get_cfg_value("notifications.pushover.user"),
            DopplerrConfig().get_cfg_value("notifications.pushover.registered_notifications"),
        )
        await po.emit(notification.notification_type, notification.notification_title,
                      notification.one_liner)
