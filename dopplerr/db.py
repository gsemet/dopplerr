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
from peewee import DateTimeField
from peewee import IntegerField
from peewee import Model
from peewee import SqliteDatabase
from peewee import TextField
from peewee import Using
from txwebbackendbase.singleton import singleton


class Events(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    type = CharField()
    message = TextField()


class MissingSubtitles(Model):
    path = CharField()
    found = BooleanField()


class FetchedSeriesSubtitles(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    series_title = CharField()
    season_number = IntegerField()
    episode_number = IntegerField()
    episode_title = CharField()
    quality = CharField()
    video_languages = CharField()
    subtitles_languages = CharField()


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

    def create_tables(self):
        self.database.create_table(MissingSubtitles, safe=True)
        self.database.create_table(Events, safe=True)
        self.database.create_table(FetchedSeriesSubtitles, safe=True)

    def insert_event(self, thetype: str, message: str):
        with Using(self.database, [Events], with_transaction=False):
            Events.insert(type=thetype, message=message).execute()

    def get_recent_events(self, limit: int):
        with Using(self.database, [Events], with_transaction=False):
            events = (Events.select().limit(limit).order_by(Events.timestamp.desc()).execute())
            return [{
                "timestamp": e.timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
                "type": e.type,
                "message": e.message
            } for e in events]

    def insert_fetched_series_subtitles(self, series_title, season_number, episode_number,
                                        episode_title, quality, video_languages,
                                        subtitles_languages):
        with Using(self.database, [FetchedSeriesSubtitles], with_transaction=True):
            FetchedSeriesSubtitles.insert(
                series_title=series_title,
                season_number=season_number,
                episode_number=episode_number,
                episode_title=episode_title,
                quality=quality,
                video_languages=video_languages,
                subtitles_languages=subtitles_languages,
            ).execute()

    def get_last_fetched_series(self, limit: int):
        with Using(self.database, [FetchedSeriesSubtitles], with_transaction=False):
            events = (FetchedSeriesSubtitles.select().limit(limit).order_by(
                FetchedSeriesSubtitles.timestamp.desc()).execute())
            return [{
                "timestamp": e.timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
                "series_title": e.series_title,
                "season_number": e.season_number,
                "episode_number": e.episode_number,
                "episode_title": e.episode_title,
                "quality": e.quality,
                "video_languages": e.video_languages,
                "subtitles_languages": e.subtitles_languages,
            } for e in events]
