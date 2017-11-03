# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from dopplerr.singleton import singleton

log = logging.getLogger(__name__)


@singleton
class DopplerrDownloader(object):
    def process_fullscan(self, _request):
        log.debug("Processing full scan of missing subtitle files...")
        res = {
            'status': 'unprocessed',
            'message': 'not implemented yet!',
        }
        # TODO: inspiration
        #   https://gist.github.com/alexsavio/9299716
        return res
