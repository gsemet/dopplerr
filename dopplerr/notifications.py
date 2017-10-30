# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import treq

from twisted.internet.defer import inlineCallbacks

from dopplerr.cfg import DopplerrConfig

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

    @inlineCallbacks
    def emit(self, notification_type, title, message):
        if not self.can_emit_notification_type(notification_type):
            log.debug("notification %s is ignored for pushover")
            return
        resp = yield treq.request(
            "POST",
            self.__api_url,
            json={
                "token": self.token,
                "user": self.user,
                "message": message,
                "title": title,
            })
        content = yield resp.text()
        log.debug("PushOver response: %r", content)


@inlineCallbacks
def emit_registered_notifications(notification_type, title, message):
    log.debug("Emiting notification: [%s] %s - %s", notification_type, title, message)
    if DopplerrConfig().get_cfg_value("notifications.pushover.enabled"):
        log.debug("Emiting pushover with user %s",
                  DopplerrConfig().get_cfg_value("notifications.pushover.user"))
        po = NotificationPushOver(
            DopplerrConfig().get_cfg_value("notifications.pushover.token"),
            DopplerrConfig().get_cfg_value("notifications.pushover.user"),
            DopplerrConfig().get_cfg_value("notifications.pushover.registered_notifications"),
        )
        yield po.emit(notification_type, title, message)
