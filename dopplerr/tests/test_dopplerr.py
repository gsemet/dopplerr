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
        # sonarr_on_download = {
        #     'EventType': 'Download',
        #     'Series': {
        #         'Id': 12,
        #         'Title': 'A Series Title',
        #         'Path': '/tv/A Series Title',
        #         'TvdbId': 123456
        #     },
        #     'Episodes': [{
        #         'Id': 1234,
        #         'EpisodeNumber': 2,
        #         'SeasonNumber': 1,
        #         'Title': 'The Episode Title',
        #         'AirDate': '2017-03-01',
        #         'AirDateUtc': '2017-03-02T02:00:00Z',
        #         'Quality': 'WEBDL-1080p',
        #         'QualityVersion': 1,
        #         'ReleaseGroup': 'ReleaseGroupName',
        #         'SceneName': 'The.Series.Title.S01E09.1080p.WEB-DL.DD5.1.H264-AGROUP-Scrambled'
        #     }]
        # }
        # '''JSON
        # {
        #     "EventType": "Download",
        #     "Series": {"Id": 28,
        #     "Title": "A Series Title",
        #     "Path": "/tv/A Series Title",
        #     "TvdbId": 123456},
        #     "Episodes": [{"Id": 1234,
        #     "EpisodeNumber": 9,
        #     "SeasonNumber": 1,
        #     "Title": "DNR",
        #     "AirDate": "2017-04-26",
        #     "AirDateUtc": "2017-04-27T01:00:00Z",
        #     "Quality": "WEBDL-1080p",
        #     "QualityVersion": 1,
        #     "ReleaseGroup": "ReleaseGroupName",
        #     "SceneName": "The.Episode.Title.S01E09.1080p.WEB-DL.DD5.1.H264-AGROUP-Scrambled"}]
        # }
        # '''
        # sonarr_filename_on_disk = ("/tv/A Series Title/Season 1/"
        #                            "The.Episode.Name.S01E09.1080p."
        #                            "WEB-DL.DD5.1.H264-AGROUP-Scrambled.mkv")
        # sonarr_on_grab = {
        #     'EventType': 'Grab',
        #     'Series': {
        #         'Id': 12,
        #         'Title': 'A Series Title',
        #         'Path': '/tv/A Series Title',
        #         'TvdbId': 123456
        #     },
        #     'Episodes': [{
        #         'Id': 1234,
        #         'EpisodeNumber': 9,
        #         'SeasonNumber': 1,
        #         'Title': 'DNR',
        #         'AirDate': '2017-04-26',
        #         'AirDateUtc': '2017-04-27T01:00:00Z',
        #         'Quality': 'WEBDL-1080p',
        #         'QualityVersion': 1,
        #         'ReleaseGroup': 'AGROUP',
        #         'SceneName': None,
        #     }]
        # }
        # Radarr
        # radarr_test = {
        #     'EventType': 'Test',
        #     'Movie': {
        #         'Id': 1,
        #         'Title': 'Test Title',
        #         'FilePath': 'C:\\testpath'
        #     },
        #     'RemoteMovie': {
        #         'TmdbId': 0,
        #         'ImdbId': 'tt012345',
        #         'Title': 'My Awesome Movie!',
        #         'Year': 0
        #     }
        # }
        # {
        #     u'EventType': u'Grab',
        #     u'RemoteMovie': {
        #       u'ImdbId': u'tt123456',
        #       u'Year': 2000,
        #       u'TmdbId': 1234,
        #       u'Title': u'Movie Name'
        #     },
        #     u'Movie': {
        #         u'FilePath': None,
        #         u'Id': 123,
        #         u'Title': u'Movie Name'
        #     }
        # }
        pass

    def test_glob_filename_with_bracket(self):
        downloader = Downloader()
        downloader.search_file("/any/root/dir", "base_name with [bracket]")
