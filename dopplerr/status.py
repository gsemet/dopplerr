# coding: utf-8

# Standard Libraries
import io
import logging

# Third Party Libraries
import aiofiles
from babelfish import Language

# Dopplerr
from dopplerr import DOPPLERR_VERSION
from dopplerr.config import DopplerrConfig
from dopplerr.singleton import singleton

log = logging.getLogger(__name__)


@singleton
class DopplerrStatus(object):

    """
    Contain current status of the application and derived values from `DopplerrConfig`.
    """

    def __init__(self):
        self.healthy = False
        self.ready = False
        self.sqlite_db_path = None
        self.subliminal_provider_configs = None
        self.previous_version = None

    def refresh_from_cfg(self):
        """
        Refresh derived values from cfg.
        """
        cfg = DopplerrConfig()
        if not cfg.get_cfg_value("general.port"):
            log.fatal("No port defined !")
            raise Exception("No port defined")
        if not cfg.get_cfg_value("general.frontenddir"):
            log.fatal("No frontend dir defined")
            raise Exception("No frontend dir defined")
        self.subliminal_provider_configs = self._build_subliminal_provider_cfgs()

        languages = cfg.get_cfg_value("subliminal.languages")
        if not languages:
            raise Exception("No languages defined")
        if any(not x for x in languages):
            raise Exception("Bad languages: {!r}".format(languages))

        if not self._check_languages(languages):
            raise Exception("Bad language defined")

        if self.previous_version is None:
            self.previous_version = cfg.get_cfg_value("general.version")
            cfg.set_cfg_value("general.version", DOPPLERR_VERSION)
        # self myself as heathly, since my conf if ok
        # i will not be ready until the loop is started and I can really start processing
        # events.
        self.healthy = True

    @property
    def has_minor_version_changed(self):
        if not self.previous_version:
            return True
        major1, _, minor_patch1 = self.previous_version.partition('.')
        major2, _, minor_patch2 = DOPPLERR_VERSION.partition('.')
        minor1, _, _patch1 = minor_patch1.partition('.')
        minor2, _, _patch2 = minor_patch2.partition('.')
        return major1 != major2 or minor1 != minor2

    def _build_subliminal_provider_cfgs(self):
        cfg = DopplerrConfig()
        provider_configs = {}
        provider_names = [
            "addic7ed",
            "legendastv",
            "opensubtitles",
            "subscenter",
        ]
        for provider_name in provider_names:
            if cfg.get_cfg_value("subliminal.{}.enabled".format(provider_name)):
                provider_configs[provider_name] = {
                    'username': cfg.get_cfg_value("subliminal.{}.user".format(provider_name)),
                    'password': cfg.get_cfg_value("subliminal.{}.password".format(provider_name)),
                }
                log.debug("Using %s username: %s", provider_name,
                          provider_configs[provider_name]['username'])
        return provider_configs

    @staticmethod
    def _check_languages(languages):
        failed = False
        for l in languages:
            try:
                Language(l)
            except ValueError:
                failed = True
                logging.critical("Invalid language: %r", l)
        if failed:
            return False
        return True

    async def get_logs(self, limit=100):
        """
        Get `limit` lines of logs in reverse order from the end of the file.
        """
        logfile = DopplerrConfig().get_cfg_value("general.logfile")
        if not logfile:
            return
        logs = []
        i = 0
        async with aiofiles.open(logfile) as fp:
            async for line in self._reverse_read_lines(fp):
                try:
                    i += 1
                    if i > limit:
                        break
                    if not line:
                        continue
                    splited_line = line.split("::")
                    if len(splited_line) < 4:
                        continue
                    dat = splited_line[0].strip()
                    level = splited_line[1].strip()
                    logger = splited_line[2].strip()
                    message = splited_line[3].strip()
                    logs.append({
                        'timestamp': dat,
                        'level': level,
                        'logger': logger,
                        'message': message,
                    })
                finally:
                    pass
        return logs

    @staticmethod
    async def _reverse_read_lines(fp, buf_size=8192):  # pylint: disable=invalid-name
        """
        Async generator that returns the lines of a file in reverse order.

        ref: https://stackoverflow.com/a/23646049/8776239
        and: https://stackoverflow.com/questions/2301789/read-a-file-in-reverse-order-using-python
        """
        segment = None  # holds possible incomplete segment at the beginning of the buffer
        offset = 0
        await fp.seek(0, io.SEEK_END)
        file_size = remaining_size = await fp.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            await fp.seek(file_size - offset)
            buffer = await fp.read(min(remaining_size, buf_size))
            remaining_size -= buf_size
            lines = buffer.splitlines(True)
            # the first line of the buffer is probably not a complete line so
            # we'll save it and append it to the last line of the next buffer
            # we read
            if segment is not None:
                # if the previous chunk starts right from the beginning of line
                # do not concat the segment to the last line of new chunk
                # instead, yield the segment first
                if buffer[-1] == '\n':
                    # print 'buffer ends with newline'
                    yield segment
                else:
                    lines[-1] += segment
                    # print 'enlarged last line to >{}<, len {}'.format(lines[-1], len(lines))
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                l = lines[index]
                if l:
                    yield l
        # Don't yield None if the file was empty
        if segment is not None:
            yield segment
