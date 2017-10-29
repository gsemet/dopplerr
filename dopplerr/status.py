# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from txwebbackendbase.singleton import singleton


@singleton
class DopplerrStatus(object):
    def __init__(self):
        self.__healthy = False
        self.__basedir = None
        self.__path_mapping = None
        self.__appdir = None
        self.__configdir = None
        self.__frontenddir = None
        self.__basedir = None
        self.__port = 0
        self.__languages = []
        self.__sqlite_db_path = None
        self.__subliminal_provider_configs = None
        self.__pushover_registered_notifications = None
        self.__pushover_user = None
        self.__pushover_token = None

    @property
    def healthy(self):
        return self.__healthy

    @healthy.setter
    def healthy(self, healthy):
        self.__healthy = healthy

    @property
    def basedir(self):
        return self.__basedir

    @basedir.setter
    def basedir(self, basedir):
        self.__basedir = basedir

    @property
    def path_mapping(self):
        return self.__path_mapping

    @path_mapping.setter
    def path_mapping(self, mapping):
        self.__path_mapping = mapping

    @property
    def appdir(self):
        return self.__appdir

    @appdir.setter
    def appdir(self, appdir):
        self.__appdir = appdir

    @property
    def configdir(self):
        return self.__configdir

    @configdir.setter
    def configdir(self, configdir):
        self.__configdir = configdir

    @property
    def frontenddir(self):
        return self.__frontenddir

    @frontenddir.setter
    def frontenddir(self, frontenddir):
        self.__frontenddir = frontenddir

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, port):
        self.__port = port

    @property
    def languages(self):
        return self.__languages

    @languages.setter
    def languages(self, languages):
        self.__languages = languages

    @property
    def sqlite_db_path(self):
        return self.__sqlite_db_path

    @sqlite_db_path.setter
    def sqlite_db_path(self, sqlite_db_path):
        self.__sqlite_db_path = sqlite_db_path

    @property
    def subliminal_provider_configs(self):
        return self.__subliminal_provider_configs

    @subliminal_provider_configs.setter
    def subliminal_provider_configs(self, provider_configs):
        self.__subliminal_provider_configs = provider_configs

    @property
    def pushover_registered_notifications(self):
        return self.__pushover_registered_notifications

    @pushover_registered_notifications.setter
    def pushover_registered_notifications(self, registered_notif):
        self.__pushover_registered_notifications = registered_notif

    @property
    def pushover_user(self):
        return self.__pushover_user

    @pushover_user.setter
    def pushover_user(self, user):
        self.__pushover_user = user

    @property
    def pushover_token(self):
        return self.__pushover_token

    @pushover_token.setter
    def pushover_token(self, token):
        self.__pushover_token = token
