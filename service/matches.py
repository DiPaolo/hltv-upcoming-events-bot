import logging
from typing import Optional, List

import schedule

import config
import hltv_parser
from domain.match_stars import MatchStars

_CACHED_MATCHES: Optional[List] = None


def init():
    if config.DEBUG:
        schedule.every(3).minutes.do(_update_cache)
    else:
        schedule.every(3).hours.do(_update_cache)

    # initial load of cache
    _update_cache()


def get_upcoming_matches():
    return _get_cache()


def get_upcoming_matches_str() -> str:
    matches = get_upcoming_matches()
    match_str_list = list()
    for match in matches:
        russian_translations = list(filter(lambda tr: tr.language.name == 'Russia', match.translations))

        if match.stars in [MatchStars.ONE, MatchStars.TWO, MatchStars.THREE, MatchStars.FOUR, MatchStars.FIVE] and \
                len(russian_translations) > 0:
            if len(russian_translations) > 1:
                translations_str = ' '.join(
                    [f"<a href='{tr.url}'>🇷🇺 {tr.streamer_name}</a>" for tr in russian_translations])
            else:
                translations_str = f"<a href='{russian_translations[0].url}'>🇷🇺</a>"
            match_str = f"{match.time_utc.hour:02}:{match.time_utc.minute:02} " \
                        f"{'*' * match.stars.value}\t{match.team1.name} - {match.team2.name} " \
                        f"({match.tournament.name}) {translations_str}"
            match_str_list.append(match_str)

    return '\n'.join(match_str_list)


def _get_cache():
    global _CACHED_MATCHES
    if not _CACHED_MATCHES:
        _update_cache()
    return _CACHED_MATCHES


def _update_cache():
    global _CACHED_MATCHES
    logging.getLogger(__name__).info('Update cache')
    _CACHED_MATCHES = hltv_parser.get_upcoming_matches()
