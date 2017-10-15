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
        self.__basedir = None
        self.__port = 0
        self.__languages = []

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
