# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import sys
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path

try:
    import colorlog
except Exception:
    colorlog = None

_namecache = {}
_inited = False


def temp_dir(name, root=None):
    root = root or tempfile.gettempdir()
    directory = Path(root) / name
    directory.mkdir(exist_ok=True)
    return directory


def setupLogger(name=None, no_color=False, level=logging.INFO, file_output=False):
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if file_output:
        if not name:
            try:
                name = Path(sys.argv[0]).absolute().with_suffix('').name
            except IndexError:
                name = None

        if name is not None and name in _namecache:
            return _namecache[name]
        log_file = Path(temp_dir(name if name else "tmp")) / "auto.log"
        file_formatter = logging.Formatter(
            '%(asctime)s :: %(levelname)s :: %(pathname)s:%(lineno)s :: %(message)s')
        file_handler = RotatingFileHandler(str(log_file), 'a', 1000000, 1)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    if no_color is False and colorlog is not None:
        stream_handler = colorlog.StreamHandler()
        colored_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(message_log_color)s%(message)s",
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
        stream_handler = logging.StreamHandler()
    root_logger.addHandler(stream_handler)
