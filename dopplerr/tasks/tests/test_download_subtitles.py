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

from pathlib import Path
from unittest import TestCase

from dopplerr.tasks.download_subtitles import DownloadSubtitleTask


class TestDownloader(TestCase):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_sonarr_notify(self):
        pass

    def assert_list_size(self, lst, size):
        if len(lst) != size:
            self.fail("list size should be {}, is {} : {}".format(size, len(lst), ", ".join(lst)))

    def test_glob_simple_filename(self):
        downloader = DownloadSubtitleTask()
        found = downloader.search_file(Path(__file__).parent / "vectors", "videofile.mp4")
        self.assert_list_size(found, 4)
        found = sorted(found)
        self.assertIn("/a_subfolder/prepended-videofile.mp4", found[0])
        self.assertIn("/a_subfolder/videofile-suffixed.mp4", found[1])
        self.assertIn("/a_subfolder/videofile.mp4", found[2])
        self.assertIn("/videofile.mp4", found[3])

    def test_glob_filename_with_bracket(self):
        downloader = DownloadSubtitleTask()
        found = downloader.search_file(Path(__file__).parent / "vectors", "complex[name].mkv")
        self.assert_list_size(found, 2)
        found = sorted(found)
        self.assertIn("vectors/a_subfolder/complex[name].mkv", found[0])
        self.assertIn("vectors/complex[name][withanothersuffix].mkv", found[1])
