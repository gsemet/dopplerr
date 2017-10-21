# -*- coding: utf-8 -*-
"""
test_dopplerr
--------------
Tests for `dopplerr` module.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# import pytest
#
from dopplerr.downloader import Downloader

# from dopplerr import dopplerr


class Testdopplerr(object):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_sonarr_notify(self):
        pass

    def test_glob_filename_with_bracket(self):
        downloader = Downloader()
        downloader.search_file("/any/root/dir", "base_name with [bracket]")
