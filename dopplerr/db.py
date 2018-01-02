# coding: utf-8

# Standard Libraries
import datetime
import logging
from pathlib import Path

# Third Party Libraries
from peewee import BooleanField
from peewee import CharField
from peewee import DateTimeField
from peewee import DoesNotExist
from peewee import ForeignKeyField
from peewee import IntegerField
from peewee import Model
from peewee import PrimaryKeyField
from peewee import TextField
from peewee import Using
from playhouse.sqliteq import SqliteQueueDatabase

# Dopplerr
from dopplerr.singleton import singleton

log = logging.getLogger(__name__)


# pylint: disable=invalid-name
class Events(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    type = CharField()
    message = TextField()


class Series(Model):
    id = PrimaryKeyField()
    tv_db_id = IntegerField(null=True)
    series_title = CharField(null=True)


class SeriesEpisodes(Model):
    id = PrimaryKeyField()
    series = ForeignKeyField(Series, related_name='episodes', null=False)
    season_number = IntegerField(null=True)
    episode_number = IntegerField(null=True)
    timestamp = DateTimeField(default=datetime.datetime.now)
    episode_title = CharField(null=True)


class SeriesMedias(Model):
    id = PrimaryKeyField()
    episode = ForeignKeyField(SeriesEpisodes, related_name='medias', null=True)
    timestamp = DateTimeField(default=datetime.datetime.now)
    quality = CharField(null=True)
    video_languages = CharField(null=True)
    dirty = BooleanField(default=True)
    media_filename = TextField(null=False, index=True)


class SeriesSubtitles(Model):
    id = PrimaryKeyField()
    media = ForeignKeyField(SeriesMedias, related_name='subtitles')
    timestamp = DateTimeField(default=datetime.datetime.now)
    language = CharField()


# pylint: enable=invalid-name


@singleton
class DopplerrDb(object):

    def __init__(self):
        self.__sqlite_db_path = None
        self.__conn = None
        self.__database = None

    @property
    def database(self):
        if not self.__database:
            self.__database = SqliteQueueDatabase(
                self.__sqlite_db_path, pragmas=(('foreign_keys', 'on'), ))
        return self.__database

    @property
    def conn(self):
        return self.database.get_conn()

    def init(self, sqlite_db_path: Path, reset_db=False):
        self.__sqlite_db_path = sqlite_db_path.as_posix()
        if reset_db:
            sqlite_db_path.unlink()

    def create_tables(self):
        self.database.create_table(Events, safe=True)
        self.database.create_table(Series, safe=True)
        self.database.create_table(SeriesEpisodes, safe=True)
        self.database.create_table(SeriesMedias, safe=True)
        self.database.create_table(SeriesSubtitles, safe=True)

    def insert_event(self, thetype: str, message: str):
        with Using(self.database, [Events], with_transaction=False):
            Events.create(type=thetype, message=message)

    def get_recent_events(self, limit: int):
        with Using(self.database, [Events], with_transaction=False):
            events = (Events.select().limit(limit).order_by(Events.timestamp.desc()).execute())
            return [{
                "timestamp": e.timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
                "type": e.type,
                "message": e.message
            } for e in events]

    def update_series_media(self,
                            series_title,
                            tv_db_id,
                            season_number,
                            episode_number,
                            episode_title,
                            quality,
                            video_languages,
                            media_filename,
                            dirty=True):
        assert media_filename, "media_filename cannot be None"
        with Using(self.database, [SeriesMedias, SeriesEpisodes, Series], with_transaction=False):
            media, _ = self._get_or_create(SeriesMedias, media_filename=media_filename)
            series, _ = self._get_or_create(
                Series,
                tv_db_id=tv_db_id,
                series_title=series_title,
            )
            _episode, _ = self._get_or_create(
                SeriesEpisodes,
                series_id=series.id,
                episode_number=episode_number,
                season_number=season_number,
                episode_title=episode_title,
            )
            media.quality = quality
            media.video_languages = video_languages
            media.dirty = dirty
            media.media_filename = media_filename
            media.save()

    @staticmethod
    def _get_or_create(model, **kwargs):
        try:
            it = model.get(**kwargs)
            return it, False
        except DoesNotExist:
            it = model.create(**kwargs)
            return it, True

    def update_fetched_series_subtitles(self, series_episode_uid, subtitles_languages, dirty=True):
        databases = [SeriesMedias, SeriesEpisodes, Series, SeriesSubtitles]
        with Using(self.database, databases, with_transaction=False):
            # yapf: disable
            medias = (
                SeriesMedias
                .select()
                .join(SeriesEpisodes)
                .join(Series)
                .where(
                    Series.tv_db_id == series_episode_uid.tv_db_id,
                    SeriesEpisodes.series == Series.id,
                    SeriesEpisodes.season_number == series_episode_uid.season_number,
                    SeriesEpisodes.episode_number == series_episode_uid.episode_number,
                    SeriesMedias.episode == SeriesEpisodes.id,
                )
            )
            # yapf: enable
            log.debug("medias=%r", medias)
            for m in medias:
                log.debug("media=%r", m)
                for lang in subtitles_languages:
                    self._get_or_create(
                        SeriesSubtitles,
                        series_media=m,
                        language=lang,
                    )
                m.dirty = dirty
                m.save()

    def get_last_fetched_series(self, limit: int):
        databases = [SeriesMedias, SeriesEpisodes, Series, SeriesSubtitles]
        with Using(self.database, databases, with_transaction=False):
            # yapf: disable
            events = (
                SeriesSubtitles
                .select()
                .order_by(SeriesSubtitles.timestamp.desc())
                .limit(limit)
                .execute()
            )
            # yapf: enable
            return [{
                "timestamp": e.timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
                "series_title": e.series_media.episode.series.series_title,
                "season_number": e.series_media.episode.season_number,
                "episode_number": e.series_media.episode.episode_number,
                "episode_title": e.series_media.episode.episode_title,
                "quality": e.series_media.quality,
                "video_languages": e.series_media.video_languages,
                "subtitle_language": e.language,
            } for e in events]

    def get_medias_series(self, limit=100):
        databases = [SeriesMedias, Series, SeriesEpisodes, SeriesSubtitles]
        with Using(self.database, databases, with_transaction=False):
            # yapf: disable
            medias = (
                SeriesMedias
                .select()
                .join(SeriesEpisodes, on=(
                    SeriesMedias.episode == SeriesEpisodes.id
                ))
                # .join(Series, on=(
                #     SeriesEpisodes.series == Series.id
                # ))
                # .join(SeriesSubtitles, on=(
                #     SeriesSubtitles.media == SeriesMedias.id
                # ))
                .order_by(SeriesMedias.timestamp)
                .limit(limit)
                .execute()
            )
            log.debug("medias=%r", "\n".join([str(med) for med in medias]))
            raise NotImplementedError
            # yapf: disable
            return [{
                "timestamp": med.timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
                "series_title": med.episode.series.series_title,
                "season_number": med.episode.season_number,
                "episode_number": med.episode.episode_number,
                "episode_title": med.episode.episode_title,
                "quality": med.quality,
                "video_languages": med.video_languages,
                "subtitle_languages": sorted(s.language for s in med.subtitles),
                "dirty": med.dirty,
            } for med in medias]

    def media_exists(self, media_filename):
        with Using(self.database, [SeriesMedias], with_transaction=False):
            # yapf: disable
            medias = (
                SeriesMedias
                .select(SeriesMedias.media_filename)
                .where(SeriesMedias.media_filename == media_filename)
                .execute()
            )
            # yapf: enable
            return bool(medias)

    def list_series(self):
        with Using(self.database, [SeriesMedias], with_transaction=False):
            # yapf: disable
            series = (
                SeriesMedias
                .select(SeriesMedias.tv_db_id, SeriesMedias.series_title, SeriesMedias.id)
                .distinct()
                .execute()
            )
            # yapf: enable
            return [{
                "id": s.id,
                "tv_db_id": s.tv_db_id,
                "series_title": s.series_title,
            } for s in series]

    def get_series(self, _seriesid):
        return None
