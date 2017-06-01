# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
"""
test_subdlsrv
-------------
Tests for `subdlsrv` module.
"""

# import pytest

# from subdlsrv import subdlsrv


class TestSubDlSrv(object):

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_sonarr_notify(self):
        # sonarr_on_download = {
        #     'EventType': 'Download',
        #     'Series': {
        #         'Id': 28,
        #         'Title': 'The 100',
        #         'Path': '/tv/The 100',
        #         'TvdbId': 268592
        #     },
        #     'Episodes': [{
        #         'Id': 2067,
        #         'EpisodeNumber': 5,
        #         'SeasonNumber': 4,
        #         'Title': 'The Tinder Box',
        #         'AirDate': '2017-03-01',
        #         'AirDateUtc': '2017-03-02T02:00:00Z',
        #         'Quality': 'WEBDL-1080p',
        #         'QualityVersion': 1,
        #         'ReleaseGroup': 'CasStudio',
        #         'SceneName': 'The.100.S04E09.1080p.WEB-DL.DD5.1.H264-RARBG-Scrambled'
        #     }]
        # }
        # '''JSON
        # {
        #     "EventType": "Download",
        #     "Series": {"Id": 28,
        #     "Title": "The 100",
        #     "Path": "/tv/The 100",
        #     "TvdbId": 268592},
        #     "Episodes": [{"Id": 2071,
        #     "EpisodeNumber": 9,
        #     "SeasonNumber": 4,
        #     "Title": "DNR",
        #     "AirDate": "2017-04-26",
        #     "AirDateUtc": "2017-04-27T01:00:00Z",
        #     "Quality": "WEBDL-1080p",
        #     "QualityVersion": 1,
        #     "ReleaseGroup": "RARBG",
        #     "SceneName": "The.100.S04E09.1080p.WEB-DL.DD5.1.H264-RARBG-Scrambled"}]
        # }
        # '''
        # sonarr_filename_on_disk = ("/tv/The 100/Season 4/"
        #                            "The.100.S04E09.1080p.WEB-DL.DD5.1.H264-RARBG-Scrambled.mkv")
        # sonarr_on_grab = {
        #     'EventType': 'Grab',
        #     'Series': {
        #         'Id': 28,
        #         'Title': 'The 100',
        #         'Path': '/tv/The 100',
        #         'TvdbId': 268592
        #     },
        #     'Episodes': [{
        #         'Id': 2071,
        #         'EpisodeNumber': 9,
        #         'SeasonNumber': 4,
        #         'Title': 'DNR',
        #         'AirDate': '2017-04-26',
        #         'AirDateUtc': '2017-04-27T01:00:00Z',
        #         'Quality': 'WEBDL-1080p',
        #         'QualityVersion': 1,
        #         'ReleaseGroup': 'RARBG',
        #         'SceneName': None,
        #     }]
        # }
        pass
