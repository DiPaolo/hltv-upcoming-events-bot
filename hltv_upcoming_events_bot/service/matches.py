import datetime
import logging
from typing import Optional, List

import schedule

from hltv_upcoming_events_bot import config
from hltv_upcoming_events_bot.service import hltv_parser
import hltv_upcoming_events_bot.db.match as db
from hltv_upcoming_events_bot.domain.match_stars import MatchStars

_CACHED_MATCHES: Optional[List] = None


def init():
    if not config.DB_USE_DB:
        _init_for_no_db_usage()


def get_upcoming_matches():
    if config.DB_USE_DB:
        logging.info('Getting upcoming matches from database')

        cur_time_utc = datetime.datetime.utcnow()
        cur_time_utc_timestamp = round(cur_time_utc.timestamp())
        tomorrow_same_time_utc = cur_time_utc + (
            datetime.timedelta(days=1) if cur_time_utc.hour < 5 else datetime.timedelta())
        tomorrow_noon_utc = datetime.datetime(year=tomorrow_same_time_utc.year, month=tomorrow_same_time_utc.month,
                                              day=tomorrow_same_time_utc.day, hour=12)
        tomorrow_noon_utc_timestamp = round(tomorrow_noon_utc.timestamp())

        matches = db.get_upcoming_matches_in_datetime_interval(cur_time_utc_timestamp, tomorrow_noon_utc_timestamp)
        return matches
    else:
        logging.info('Getting upcoming matches from local cache not using database')
        return _get_cache_no_db_usage()


def get_upcoming_matches_str() -> str:
    matches = get_upcoming_matches()
    match_str_list = list()

    # remove all unnecessary (non-target) matches to make it easier to apply
    # the logic of tournament description (one for all matches or tournament name per each match)
    tournaments_names = set()
    target_matches = list()
    for match in matches:
        russian_translations = list(filter(lambda tr: tr.language.name == 'Russia', match.translations))
        if match.stars != MatchStars.ZERO and len(russian_translations) > 0:
            target_matches.append(match)
            tournaments_names.add(match.tournament.name)

    for match in target_matches:
        russian_translations = list(filter(lambda tr: tr.language.name == 'Russia', match.translations))

        translations_str = ' '.join(
            [f"<a href='{tr.url}'>🎥 {tr.streamer_name}</a>" for tr in russian_translations])

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


def _init_for_no_db_usage():
    if config.DEBUG:
        schedule.every(3).minutes.do(_update_cache_no_db_usage)
    else:
        schedule.every(3).hours.do(_update_cache_no_db_usage)

    # initial load of cache
    _update_cache_no_db_usage()


def _get_cache_no_db_usage():
    global _CACHED_MATCHES
    if not _CACHED_MATCHES:
        _update_cache_no_db_usage()
    return _CACHED_MATCHES


def _update_cache_no_db_usage():
    global _CACHED_MATCHES
    logging.info('Update cache')

    # use try/except because if something goes wrong inside, the scheduler will
    # not emit the event next time
    try:
        _CACHED_MATCHES = hltv_parser.get_upcoming_matches()
    except Exception as ex:
        logging.error(f'Exception while updating cache with upcoming matches: {ex}')
