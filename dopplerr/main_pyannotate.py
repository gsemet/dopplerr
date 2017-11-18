# coding: utf-8

# Standard Libraries
import logging

# Third Party Libraries
from pyannotate_runtime import collect_types

# Dopplerr
from dopplerr.main import main

log = logging.getLogger(__name__)


def main_pyannotate():
    try:
        collect_types.init_types_collection()
        collect_types.resume()
        return main()
    finally:
        log.info("dumping type_info")
        collect_types.pause()
        collect_types.dump_stats('type_info.json')


if __name__ == '__main__':
    main_pyannotate()
