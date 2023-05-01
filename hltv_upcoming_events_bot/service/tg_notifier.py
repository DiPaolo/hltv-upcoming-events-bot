import logging
from enum import Enum

import schedule

import hltv_upcoming_events_bot.service.db as db_service
from hltv_upcoming_events_bot import config
from hltv_upcoming_events_bot.service.matches import get_upcoming_matches_str

_SEND_MESSAGE_FUNC = None


class RetCode(Enum):
    OK = 1
    ERROR = 2
    NOT_EXIST = 3
    ALREADY_EXIST = 4


def init(send_message_func):
    global _SEND_MESSAGE_FUNC

    if config.DEBUG:
        schedule.every(2).minutes.do(_notify_subscribers)
    else:
        schedule.every().day.at("09:10:00").do(_notify_subscribers)

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
        logging.error(f'unhandled value returned from subscribe_chat_by_telegram_id(): {ret}')
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
        logging.error(f'unhandled value returned from unsubscribe_chat_by_telegram_id(): {ret}')
        return RetCode.ERROR


def _notify_subscribers():
    logging.getLogger(__name__).info('Notify subscribers')

    if not _SEND_MESSAGE_FUNC:
        logging.getLogger(__name__).error('Failed to notify subscribers because ')
        return

    # use try/except because if something goes wrong inside, the scheduler will
    # not emit the event next time
    try:
        msg = get_upcoming_matches_str()
        for subs in db_service.get_subscribers():
            try:
                _SEND_MESSAGE_FUNC(subs.telegram_id, msg)
            except Exception as ex:
                logging.error(f'Exception while notifying subscriber (telegram_id={subs.telegram_id}): {ex}')
    except Exception as ex:
        logging.error(f'Exception while getting upcoming matches text: {ex}')
