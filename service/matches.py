import logging
import pickle
import threading
import time
from typing import Optional, List

import config
import schedule

import domain.match
import hltv_parser


_PICKLE_FILENAME = '.matches_cache'
_CACHED_MATCHES: Optional[List] = None


class ScheduleThread(threading.Thread):
    @classmethod
    def run(cls):
        while True:
            schedule.run_pending()
            time.sleep(1)


def init():
    if config.DEBUG:
        schedule.every(3).minutes.do(_update_cache)
    else:
        schedule.every(3).hours.do(_update_cache)

    continuous_thread = ScheduleThread()
    continuous_thread.start()

    # initial load of cache
    _update_cache()


def get_upcoming_matches():
    return _get_cache()


def _get_cache():
    global _CACHED_MATCHES
    if not _CACHED_MATCHES:
        _update_cache()
    return _CACHED_MATCHES


def _update_cache():
    global _CACHED_MATCHES
    logging.getLogger(__name__).info('Update cache')
    _CACHED_MATCHES = hltv_parser.get_upcoming_matches()


def _cleanup_cache():
    global _CACHED_MATCHES
    logging.getLogger(__name__).info('Clean-up cache')
    _CACHED_MATCHES = None
