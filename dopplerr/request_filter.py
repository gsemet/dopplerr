# coding: utf-8

import logging

from dopplerr.config import DopplerrConfig

log = logging.getLogger(__name__)


class _FilterBase(object):
    def appy_path_mapping(self, folder):
        if not DopplerrConfig().get_cfg_value("general.mapping"):
            return folder
        if folder.startswith("/"):
            absolute = True
            folder = folder[1:]
        for mapping in DopplerrConfig().get_cfg_value("general.mapping"):
            log.debug("Mapping: %s", mapping)
            k, _, v = mapping.partition("=")
            log.debug("Applying mapping %s => %s", k, v)
            if folder.startswith(k):
                folder = v + folder[len(k):]
                break
        if absolute:
            return "/" + folder
        return folder

    @staticmethod
    def lowerize_dick_keys(thedict):
        return {k.lower(): v for k, v in thedict.items()}


#
# class AutoDetectFilter(_FilterBase):
#     def filter(self, request, res):
#         low_request = self.lowerize_dick_keys(request)
#         if "series" in low_request:
#             return SonarrFilter().filter(request, res)
#         return res.failed("Unable to find request type")
