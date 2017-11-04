# coding: utf-8

import logging

import aiohttp

from dopplerr.notifications._base import _NotificationBase

log = logging.getLogger(__name__)


class NotificationPushOver(_NotificationBase):

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
            d = {
                "token": self.token,
                "user": self.user,
                "message": message,
                "title": title,
            }
            async with session.post(self.__api_url, data=d) as result:
                response = await result.json()
                log.debug("PushOver response: %r", response)
