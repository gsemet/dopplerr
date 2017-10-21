# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sqlite3
from pathlib import Path

from txwebbackendbase.singleton import singleton


@singleton
class DopplerrDb(object):
    def __init__(self):
        self.__sqlite_db_path = None
        self.__conn = None

    @property
    def conn(self):
        if not self.__conn:
            self.__conn = sqlite3.connect(self.__sqlite_db_path)
        return self.__conn

    def createTables(self, sqlite_db_path: Path):
        self.__sqlite_db_path = sqlite_db_path.as_posix()
        self.conn.execute("""
            CREATE TABLE iF NOT EXISTS missing_subtitle(filename text)
             """)
