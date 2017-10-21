# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
# import sqlite3
import threading
from pathlib import Path

# from peewee import ForeignKeyField
from peewee import BooleanField
from peewee import CharField
from peewee import DateTimeField, Using
from peewee import Model
from peewee import SqliteDatabase
from peewee import TextField
from txwebbackendbase.singleton import singleton


class Events(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    type = CharField()
    message = TextField()


class MissingSubtitles(Model):
    path = CharField()
    found = BooleanField()


@singleton
class DopplerrDb(object):
    def __init__(self):
        self.__sqlite_db_path = None
        self.__conn = None
        self.__database = None
        self.__db_lock = threading.Lock()

    @property
    def database(self):
        if not self.__database:
            self.__database = SqliteDatabase(self.__sqlite_db_path)
        return self.__database

    @property
    def conn(self):
        return self.database.get_conn()

    def init(self, sqlite_db_path: Path):
        self.__sqlite_db_path = sqlite_db_path.as_posix()

    def createTables(self):
        self.database.create_table(MissingSubtitles, safe=True)
        self.database.create_table(Events, safe=True)

    def insertEvent(self, thetype: str, message: str):
        with Using(self.database, [Events], with_transaction=False):
            Events.insert(type=thetype, message=message).execute()

    def getLastEvents(self, limit: int):
        with Using(self.database, [Events], with_transaction=False):
            events = (Events.select().limit(limit).order_by(Events.timestamp.desc()).execute())
            return [{
                "timestamp": e.timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
                "type": e.type,
                "message": e.message
            } for e in events]
