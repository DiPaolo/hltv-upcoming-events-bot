import logging
from typing import Optional, List

import schedule

from hltv_upcoming_events_bot import hltv_parser, config
from hltv_upcoming_events_bot.domain.match_stars import MatchStars

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

    # remove all unnecessary (non-target) matches to make it easier to apply
    # the logic of tournament description (one for all matches or tournamet name per each match)
    tournaments_names = set()
    target_matches = list()
    for match in matches:
        russian_translations = list(filter(lambda tr: tr.language.name == 'Russia', match.translations))
        if match.stars != MatchStars.ZERO and len(russian_translations) > 0:
            target_matches.append(match)
            tournaments_names.add(match.tournament.name)

    for match in target_matches:
        russian_translations = list(filter(lambda tr: tr.language.name == 'Russia', match.translations))

        translations_str = ''
        if len(russian_translations) > 1:
            translations_str = ' '.join(
                [f"<a href='{tr.url}'>{tr.streamer_name}🎥</a>" for tr in russian_translations])
        elif len(russian_translations) > 0:
            translations_str = f"<a href='{russian_translations[0].url}'>🎥</a>"

        tournament_name_str = f"({match.tournament.name})" if len(tournaments_names) != 1 else ''

        match_str = f"{match.time_utc.hour:02}:{match.time_utc.minute:02} " \
                    f"{'⭐' * match.stars.value}\t{match.team1.name} - {match.team2.name} " + \
                    f"{tournament_name_str} {translations_str}"
        match_str_list.append(match_str)

    msg = ''
    if len(tournaments_names) == 1:
        msg += f'Сегодня игры <b>{tournaments_names.pop()}</b>\n\n'

    msg += '\n\n'.join(match_str_list)
    return msg


def _get_cache():
    global _CACHED_MATCHES
    if not _CACHED_MATCHES:
        _update_cache()
    return _CACHED_MATCHES


def _update_cache():
    global _CACHED_MATCHES
    logging.getLogger(__name__).info('Update cache')
    _CACHED_MATCHES = hltv_parser.get_upcoming_matches()
