# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import glob
import sys


def recursive_iglob_fallback(path):
    try:
        # pylint: disable=import-error
        import glob2
        # pylint: enable=import-error
    except Exception:
        raise Exception("glob2 not installed on your environment !")
    return glob2.iglob(path, with_matches=True)


def recursive_iglob(path):
    if sys.version_info < (3, 5):
        return recursive_iglob_fallback(path)
    return glob.iglob(path, recursive=True)
