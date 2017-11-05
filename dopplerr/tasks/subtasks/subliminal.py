# coding: utf-8

import logging
import os

from babelfish import Language
from subliminal import Video
from subliminal import download_best_subtitles
from subliminal import region
from subliminal import save_subtitles
from subliminal.subtitle import get_subtitle_path

from dopplerr.tasks.threaded import ThreadedTask

log = logging.getLogger(__name__)


class SubliminalTask(ThreadedTask):
    worker_threads_num = 1

    async def _run(self, res):
        raise NotImplementedError

    @staticmethod
    def initialize_db():
        log.info("Initializing Subliminal cache...")
        region.configure('dogpile.cache.dbm', arguments={'filename': 'cachefile.dbm'})

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
