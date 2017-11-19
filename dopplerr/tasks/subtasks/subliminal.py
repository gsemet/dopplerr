# coding: utf-8

# Standard Libraries
import logging
import os
from datetime import timedelta

# Third Party Libraries
from babelfish import Language
from subliminal import Episode
from subliminal import Movie
from subliminal import Video
from subliminal import download_best_subtitles
from subliminal import refine
from subliminal import refiner_manager
from subliminal import region
from subliminal import save_subtitles
from subliminal.cli import MutexLock
from subliminal.subtitle import get_subtitle_path

# Dopplerr
from dopplerr.descriptors.series import SeriesEpisodeInfo
from dopplerr.descriptors.series import SeriesEpisodeUid
from dopplerr.tasks.threaded import ThreadedTask

log = logging.getLogger(__name__)


class SubliminalSubDownloader(ThreadedTask):
    worker_threads_num = 1

    async def _run(self, res):
        raise NotImplementedError

    @staticmethod
    def initialize_db():
        log.info("Initializing Subliminal cache...")
        region.configure(
            'dogpile.cache.dbm',
            expiration_time=timedelta(days=30),
            arguments={
                'filename': 'cachefile.dbm',
                'lock_factory': MutexLock
            })

    # async def download_sub_by_subproc(self, videos, languages, provider_configs):
    #     subl_cmd = ["subliminal"]
    #     print(provider_configs)
    #     for provider_name, provider_config in provider_configs.items():
    #         subl_cmd.extend([
    #             "--{}".format(provider_name),
    #             provider_config['username'],
    #             provider_config['password'],
    #         ])
    #     subl_cmd.extend(["download"])
    #     for l in languages:
    #         subl_cmd.extend(["--language", l])
    #     subl_cmd.extend(videos)
    #     subl_cmd.extend(["-vvv"])
    #     stdout, stderr, code = await self._run_command(*subl_cmd)
    #     log.debug(stdout)
    #     log.error(stderr)
    #     log.error(code)
    #     if "Downloaded 0 subtitle" in stdout:
    #         log.error("No subtitle downloaded")
    #     raise NotImplementedError

    async def download_sub(self, videos, languages, provider_configs):
        return await self._run_in_thread(
            download_best_subtitles,
            videos, {Language(l)
                     for l in languages},
            provider_configs=provider_configs)

    @staticmethod
    def filter_video_files(files):
        videos = []
        for fil in files:
            _, ext = os.path.splitext(fil)
            if ext in [".jpeg", ".jpg", ".nfo", ".srt", ".sub", ".nbz"]:
                log.debug("Ignoring %s because of extension: %s", fil, ext)
                continue
            videos.append(Video.fromname(fil))
        return videos

    @staticmethod
    def get_subtitle_path(video_file, language):
        return get_subtitle_path(video_file, language=language)

    @staticmethod
    def save_subtitles(video, subtitle_info):
        return save_subtitles(video, subtitle_info)


class RefineVideoFileTask(ThreadedTask):

    async def refine_file(self, video_file):
        return await self._run_in_thread(self._refine_file, video_file)

    @staticmethod
    def _refine_file(video_file):
        log.debug("Refining file %s", video_file)
        try:
            video = Video.fromname(video_file)
        except ValueError:
            log.error("Cannot guess video file type from: %s", video_file)
            return
        refiner = sorted(refiner_manager.names())
        refine(video, episode_refiners=refiner, movie_refiners=refiner)
        log.debug("refine result: %r", video)
        if isinstance(video, Episode):
            log.debug("series: %s", video.series)
            log.debug("season: %s", video.season)
            log.debug("episode: %s", video.episode)
            log.debug("title: %s", video.title)
            log.debug("series_tvdb_id: %s", video.series_tvdb_id)
            return SeriesEpisodeInfo(
                series_episode_uid=SeriesEpisodeUid(
                    tv_db_id=video.series_tvdb_id,
                    season_number=video.season,
                    episode_number=video.episode,
                ),
                series_title=video.series,
                episode_title=video.title,
                quality=None,
                video_languages=None,
                subtitles_languages=None,
                media_filename=video_file,
                dirty=True,
            )
        elif isinstance(video, Movie):
            log.debug("movie: %s", video.title)
