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


DEFAULT_FILE_FMT = '%(asctime)s :: %(levelname)-8s :: %(pathname)s:%(lineno)s :: %(message)s'
DEFAULT_COLOR_FMT = ("%(log_color)s%(levelname)-8s%(reset)s " "%(message_log_color)s%(message)s")
DEFAULT_COLOR_DATE_FMT = "%(asctime)s " + DEFAULT_COLOR_FMT
DEFAULT_FMT = "%(levelname)-8s %(message)s"
DEFAULT_DATE_FMT = "%(asctime)s " + DEFAULT_FMT

g_file_handler = None
g_stream_handler = None


def setupLogger(no_color=False,
                level=logging.INFO,
                logfile=None,
                show_time=True,
                file_fmt=DEFAULT_FILE_FMT,
                color_fmt=DEFAULT_COLOR_FMT,
                color_date_fmt=DEFAULT_COLOR_DATE_FMT,
                fmt=DEFAULT_FMT,
                date_fmt=DEFAULT_DATE_FMT):
    """
    Simple yet efficient logger configuration utility.

    4 satisfying flavors of format string are provided:
    - no date, no color
    - date, no color
    - no date, color
    - data, color

    Typically, you call this method as soon as possible in your application, so you have logs
    on your terminal. Then you recall it with options, depending on your application configuration
    (ex: verbose, output to log file, ...)

    Usage:
    ```
    def main():
        setupLogger()
        ...
        # read command line argument
        verbose = opt/argparse.verbose
        setupLogger(level=logging.DEBUG is verbose else logging.INFO)
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

    if no_color is False and colorlog is not None:
        if show_time:
            format_str = color_date_fmt
        else:
            format_str = color_fmt
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
        if show_time:
            format_str = date_fmt
        else:
            format_str = fmt
        stream_handler = logging.StreamHandler()
        stream_formatter = logging.Formatter(format_str)
        stream_handler.setFormatter(stream_formatter)
    if g_stream_handler:
        root_logger.removeHandler(g_stream_handler)
    root_logger.addHandler(stream_handler)
    g_stream_handler = stream_handler
