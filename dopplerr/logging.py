# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path

# pylint: disable=import-error
try:
    import colorlog
except Exception:
    colorlog = None
# pylint: enable=import-error


def temp_dir(name, root=None):
    root = root or tempfile.gettempdir()
    directory = Path(root) / name
    directory.mkdir(exist_ok=True)
    return directory


class ColorCmd(object):
    LOG_COLOR = "%(log_color)s"
    RESET = "%(reset)s"
    MSG_COLOR = "%(message_log_color)s"


class StdOutLogChunks(object):
    DATE = "%(asctime)19s"
    LEVEL = "[ %(levelname)-8s ]"
    NAME = "[ %(name)-25s ]"
    MESSAGE = "%(message)s"


class StdOutColorLogChunks(object):
    DATE = StdOutLogChunks.DATE
    LEVEL = ColorCmd.LOG_COLOR + "%(white)s[ %(reset)s%(levelname)-8s%(white)s ]%(reset)s"
    NAME = ColorCmd.LOG_COLOR + "%(white)s[ %(reset)s%(name)-25s%(white)s ]%(reset)s"
    MESSAGE = ColorCmd.MSG_COLOR + StdOutLogChunks.MESSAGE + ColorCmd.RESET


class StdOutLog(object):
    color_fmt = "{date} {name} {level} {message}".format(
        date=StdOutColorLogChunks.DATE,
        level=StdOutColorLogChunks.LEVEL,
        message=StdOutColorLogChunks.MESSAGE,
        name=StdOutColorLogChunks.NAME,
    )
    no_color_fmt = "{date} {name} {level} {message}".format(
        date=StdOutLogChunks.DATE,
        level=StdOutLogChunks.LEVEL,
        message=StdOutLogChunks.MESSAGE,
        name=StdOutLogChunks.NAME,
    )


class DefaultFileFmtChunks(object):
    DATE = "%(asctime)s"
    LEVELNAME = "%(levelname)-8s"
    FILE_LINE = "%(pathname)s:%(lineno)s"
    MESSAGE = "%(message)s"


class DefaultFileFmt(object):
    fmt = " :: ".join([
        DefaultFileFmtChunks.DATE,
        DefaultFileFmtChunks.LEVELNAME,
        DefaultFileFmtChunks.FILE_LINE,
        DefaultFileFmtChunks.MESSAGE,
    ])


g_file_handler = None
g_stream_handler = None


def setup_logger(
        color=True,
        level=logging.INFO,
        logfile=None,
        file_fmt=DefaultFileFmt.fmt,
        stdout_color_fmt=StdOutLog.color_fmt,
        stdout_fmt=StdOutLog.no_color_fmt,
):
    """
    Simple yet efficient logger configuration utility.

    Typically, you call this method as soon as possible in your application, so you have logs
    on your terminal. Then you recall it with options, depending on your application configuration
    (ex: verbose, output to log file, ...)

    Usage:
    ```
    def main():
        setup_logger()
        ...
        # read command line argument
        verbose = opt/argparse.verbose
        setup_logger(level=logging.DEBUG is verbose else logging.INFO)
    ```
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    global g_file_handler
    global g_stream_handler

    if logfile:
        file_formatter = logging.Formatter(file_fmt)
        file_handler = RotatingFileHandler(str(logfile), 'a', 5 * 1024 * 1024, 1)
        file_handler.setFormatter(file_formatter)
        if g_file_handler:
            root_logger.removeHandler(g_file_handler)
        root_logger.addHandler(file_handler)
        g_file_handler = file_handler

    if color and colorlog is not None:
        format_str = stdout_color_fmt
        stream_handler = colorlog.StreamHandler()
        colored_formatter = colorlog.ColoredFormatter(
            format_str,
            log_colors={
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
                'DEBUG': 'cyan',
            },
            secondary_log_colors={
                'message': {
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                    'DEBUG': 'cyan',
                }
            })
        stream_handler.setFormatter(colored_formatter)
    else:
        format_str = stdout_fmt
        stream_handler = logging.StreamHandler()
        stream_formatter = logging.Formatter(format_str)
        stream_handler.setFormatter(stream_formatter)
    if g_stream_handler:
        root_logger.removeHandler(g_stream_handler)
    root_logger.addHandler(stream_handler)
    g_stream_handler = stream_handler
