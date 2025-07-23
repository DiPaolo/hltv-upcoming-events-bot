import datetime
import logging
from enum import Enum
from typing import Callable, Optional

import schedule

import hltv_upcoming_events_bot.service.db as db_service
import hltv_upcoming_events_bot.service.news as news_service
from hltv_upcoming_events_bot import config
from hltv_upcoming_events_bot.service.matches import get_upcoming_matches_str

_SEND_MESSAGE_FUNC: Optional[Callable] = None
_logger = logging.getLogger('hltv_upcoming_events_bot.service.tg_notifier')


class RetCode(Enum):
    OK = 1
    ERROR = 2
    NOT_EXIST = 3
    ALREADY_EXIST = 4


def init(send_message_func: Callable):
    global _SEND_MESSAGE_FUNC

    if config.DEBUG:
        schedule.every(2).minutes.do(_notify_subscribers_about_matches)
        schedule.every(3).minutes.do(_notify_subscribers_about_news, 24, 5)
    else:
        # Moscow time (UTC+3)
        schedule.every().day.at("09:10:00").do(_notify_subscribers_about_matches)
        schedule.every().day.at("06:05:00").do(_notify_subscribers_about_news, 24, 5)
        schedule.every().day.at("18:05:00").do(_notify_subscribers_about_news, 12, 3)

    _SEND_MESSAGE_FUNC = send_message_func


def add_subscriber(tg_id: int) -> RetCode:
    ret = db_service.subscribe_chat_by_telegram_id(tg_id)
    if ret == db_service.RetCode.OK:
        return RetCode.OK
    elif ret == db_service.RetCode.ERROR:
        return RetCode.ERROR
    elif ret == db_service.RetCode.ALREADY_EXIST:
        return RetCode.ALREADY_EXIST
    else:
        _logger.error(f'unhandled value returned from subscribe_chat_by_telegram_id(): {ret}')
        return RetCode.ERROR


def remove_subscriber(tg_id: int):
    ret = db_service.unsubscribe_chat_by_telegram_id(tg_id)
    if ret == db_service.RetCode.OK:
        return RetCode.OK
    elif ret == db_service.RetCode.ERROR:
        return RetCode.ERROR
    elif ret == db_service.RetCode.NOT_EXIST:
        return RetCode.NOT_EXIST
    else:
        _logger.error(f'unhandled value returned from unsubscribe_chat_by_telegram_id(): {ret}')
        return RetCode.ERROR


def _notify_subscribers_about_matches():
    _logger.info('Notify subscribers about matches')

    if not _SEND_MESSAGE_FUNC:
        _logger.error('Failed to notify subscribers about matches')
        return

    # use try/except because if something goes wrong inside, the scheduler will
    # not emit the event next time
    try:
        msg = get_upcoming_matches_str()
        for subs in db_service.get_subscribers():
            try:
                _SEND_MESSAGE_FUNC(subs.telegram_id, msg)
            except Exception as ex:
                _logger.error(
                    f'Exception while notifying subscriber about matches (telegram_id={subs.telegram_id}): {ex}')
    except Exception as ex:
        _logger.error(f'Exception while getting upcoming matches text: {ex}')


def _notify_subscribers_about_news(for_last_n_hours: int, news_count: int):
    _logger.info('Notify subscribers about news')

    if not _SEND_MESSAGE_FUNC:
        _logger.error('Failed to notify subscribers about news')
        return

    # use try/except because if something goes wrong inside, the scheduler will
    # not emit the event next time
    for subs in db_service.get_subscribers():
        try:
            news_items = news_service.get_recent_news_for_chat(config.GAME_TYPE,
                subs.telegram_id, datetime.datetime.utcnow() - datetime.timedelta(hours=for_last_n_hours), news_count)
        except Exception as ex:
            _logger.error(f'Exception while getting recent news text: {ex}')
            continue

        msg = news_service.get_recent_news_str(news_items)

        try:
            _SEND_MESSAGE_FUNC(subs.telegram_id, msg)
            db_service.mark_news_items_as_sent(news_items, [subs.telegram_id], datetime.datetime.utcnow())
        except Exception as ex:
            _logger.error(f'Exception while notifying subscriber about news (telegram_id={subs.telegram_id}): {ex}')
