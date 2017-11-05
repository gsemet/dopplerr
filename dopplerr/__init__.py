# coding: utf-8

import platform

import pbr.version

__version__ = pbr.version.VersionInfo('dopplerr').release_string()
VERSION = __version__
DOPPLERR_VERSION = __version__

APSSCHEDULER_VERSION = pbr.version.VersionInfo('apscheduler').release_string()
PYTHON_VERSION = platform.python_version()
SANIC_VERSION = pbr.version.VersionInfo('sanic').release_string()

__all__ = [
    '__version__',
    'APSSCHEDULER_VERSION',
    'DOPPLERR_VERSION',
    'PYTHON_VERSION',
    'SANIC_VERSION',
    'VERSION',
]
