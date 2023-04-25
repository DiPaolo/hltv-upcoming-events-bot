import datetime
import logging
from typing import Optional, List

import schedule

import hltv_upcoming_events_bot.service.db as db_service
from hltv_upcoming_events_bot import config, domain
from hltv_upcoming_events_bot.service import hltv_parser

_CACHED_MATCHES: Optional[List] = None


def init():
    _setup_schedule()


def get_upcoming_matches() -> List[domain.Match]:
    logging.info('Getting upcoming matches from database')

    cur_time_utc = datetime.datetime.utcnow()
    cur_time_utc_timestamp = round(cur_time_utc.timestamp())
    tomorrow_same_time_utc = cur_time_utc + (
        datetime.timedelta(days=1) if cur_time_utc.hour >= 1 else datetime.timedelta())
    tomorrow_noon_utc = datetime.datetime(year=tomorrow_same_time_utc.year, month=tomorrow_same_time_utc.month,
                                          day=tomorrow_same_time_utc.day, hour=12)
    tomorrow_noon_utc_timestamp = round(tomorrow_noon_utc.timestamp())

    matches = db_service.get_upcoming_matches_in_datetime_interval(cur_time_utc_timestamp, tomorrow_noon_utc_timestamp)
    return matches


def get_upcoming_matches_str() -> str:
    matches = get_upcoming_matches()
    match_str_list = list()

    # remove all unnecessary (non-target) matches to make it easier to apply
    # the logic of tournament description (one for all matches or tournament name per each match)
    tournaments_names = set()
    target_matches = list()
    for match in matches:
        russian_translations = list(filter(lambda s: s.language == 'Russia', match.streamers))
        if match.stars.value != domain.MatchStars.ZERO.value and len(russian_translations) > 0:
            target_matches.append(match)
            tournaments_names.add(match.tournament.name)

    for match in target_matches:
        russian_translations = list(filter(lambda s: s.language == 'Russia', match.streamers))

        translations_str = ' '.join(
            [f"<a href='{s.url}'>🎥 {s.name}</a>" for s in russian_translations])

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


def _setup_schedule():
    if config.DEBUG:
        schedule.every(3).minutes.do(_do_job)
    else:
        schedule.every(4).to(6).hours.do(_do_job)

    # initial load of cache
    _do_job()


def _do_job():
    logging.info("Getting the list of today's matches")

    matches = _parse_upcoming_matches()
    _add_matches_to_db(matches)


def _parse_upcoming_matches() -> List[domain.Match]:
    # use try/except because if something goes wrong inside, the scheduler will
    # not emit the event next time
    matches = list()
    try:
        matches = hltv_parser.get_upcoming_matches()
    except Exception as ex:
        logging.error(f'Exception while updating cache with upcoming matches: failed to get upcoming matches: {ex}')

    return matches


def _add_matches_to_db(matches: List[domain.Match]):
    for match in matches:
        try:
            for match_streamer in match.streamers:
                db_service.add_streamer(match_streamer)
            db_service.add_match(match)
        except Exception as ex:
            logging.error(f'Exception while updating cache with upcoming matches: failed to add match (url={match.url}): {ex}')
