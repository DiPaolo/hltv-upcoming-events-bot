import logging

import schedule

import hltv_upcoming_events_bot.service.db as db_service
from hltv_upcoming_events_bot import config
from hltv_upcoming_events_bot.service.matches import get_upcoming_matches_str

_SEND_MESSAGE_FUNC = None


def init(send_message_func):
    global _SEND_MESSAGE_FUNC

    if config.DEBUG:
        schedule.every(2).minutes.do(_notify_subscribers)
    else:
        schedule.every().day.at("09:10:00").do(_notify_subscribers)

    _SEND_MESSAGE_FUNC = send_message_func


def add_subscriber(tg_id: int):
    db_service.subscribe_user_by_telegram_id(tg_id)


def remove_subscriber(tg_id: int):
    db_service.unsubscribe_user_by_telegram_id(tg_id)


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
