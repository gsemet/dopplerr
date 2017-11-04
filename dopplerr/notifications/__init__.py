# coding: utf-8

import logging

from dopplerr.notifications.pushover import NotificationPushOver
from dopplerr.config import DopplerrConfig

log = logging.getLogger(__name__)


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
