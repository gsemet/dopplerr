# coding: utf-8

import logging
from collections import namedtuple

log = logging.getLogger(__name__)

SeriesEpisodeUid = namedtuple('SeriesEpisodeUid', ['tv_db_id', 'season_number', 'episode_number'])

SeriesEpisodeInfo = namedtuple('SeriesEpisodeInfo', [
    'series_episode_uid',
    'episode_title',
    'quality',
    'video_languages',
    'subtitles_languages',
    'media_filename',
    'dirty',
])
