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


def get_upcoming_translations() -> List[domain.Translation]:
    logging.info('Getting upcoming matches from database')

    cur_time_utc = datetime.datetime.utcnow()
    cur_time_utc_timestamp = round(cur_time_utc.timestamp())
    tomorrow_same_time_utc = cur_time_utc + (
        datetime.timedelta(days=1) if cur_time_utc.hour >= 1 else datetime.timedelta())
    tomorrow_noon_utc = datetime.datetime(year=tomorrow_same_time_utc.year, month=tomorrow_same_time_utc.month,
                                          day=tomorrow_same_time_utc.day, hour=12)
    tomorrow_noon_utc_timestamp = round(tomorrow_noon_utc.timestamp())

    translations = db_service.get_translations_in_period(cur_time_utc_timestamp, tomorrow_noon_utc_timestamp)
    return translations


def get_upcoming_matches_str() -> str:
    translations = get_upcoming_translations()
    match_str_list = list()

    # the list of translations that we've got is not grouped;
    # so we have to group translations by matches (one match -> zero, one, or more streamers)

    # match's url is used as a key in the dict;
    # value is a tuple of match + list of streamers
    # will be filtered (non-target matches are out of the dict)
    matches = dict()

    tournaments_names = set()
    for trans in translations:
        is_target_translation = trans.streamer.language == 'Russia'
        if trans.match.stars.value == domain.MatchStars.ZERO.value or not is_target_translation:
            continue

        tournaments_names.add(trans.match.tournament.name)

        if trans.match.url not in matches:
            matches[trans.match.url] = (trans.match, [trans.streamer])
        else:
            matches[trans.match.url][1].append(trans.streamer)

    for match, streamers in matches.values():
        translations_str = ' '.join([f"<a href='{s.url}'>🎥 {s.name}</a>" for s in streamers])
        tournament_name_str = f"(<b>{match.tournament.name}</b>)" if len(tournaments_names) != 1 else ''

        # use UTC+7 timezone
        user_time = match.time_utc.astimezone(datetime.timezone(datetime.timedelta(hours=7)))

        match_str = f"{user_time.hour:02}:{user_time.minute:02} " \
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
        schedule.every(3).minutes.do(populate_translations)
    else:
        schedule.every(4).to(6).hours.do(populate_translations)

    # initial load of cache
    populate_translations()


def populate_translations():
    logging.info("Getting the list of today's matches")

    translations = _parse_upcoming_translations()
    _add_translations_to_db(translations)


def _parse_upcoming_translations() -> List[domain.Translation]:
    # use try/except because if something goes wrong inside, the scheduler will
    # not emit the event next time
    translations = list()
    try:
        translations = hltv_parser.get_upcoming_translations()
    except Exception as ex:
        logging.error(f'Exception while updating cache with upcoming matches: failed to get upcoming matches: {ex}')

    return translations


def _add_translations_to_db(translations: List[domain.Translation]):
    for trans in translations:
        try:
            db_service.add_translation(trans.match, trans.streamer)
        except Exception as ex:
            logging.error(
                f'Exception while updating cache with upcoming matches: failed to add translation '
                f'(match_url={trans.match.url}, streamer_url={trans.streamer.url}): {ex}')
