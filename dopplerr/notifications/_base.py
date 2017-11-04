# coding: utf-8

import logging

log = logging.getLogger(__name__)


class _NotificationBase(object):

    NOTIFICATION_TYPES = ["fetched"]

    def __init__(self, registered_notification):
        self._registered_notification = registered_notification

    def can_emit_notification_type(self, requested_notif_type):
        return requested_notif_type in self._registered_notification
