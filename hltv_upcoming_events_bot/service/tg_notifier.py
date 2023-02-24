import logging
import pickle

import schedule
from hltv_upcoming_events_bot import config
from hltv_upcoming_events_bot.service.matches import get_upcoming_matches_str

_SUBSCRIBERS = set()
_PICKLE_FILENAME = '.subscribers'
_SEND_MESSAGE_FUNC = None


def init(send_message_func):
    global _SUBSCRIBERS
    global _SEND_MESSAGE_FUNC

    if config.DEBUG:
        schedule.every(2).minutes.do(_notify_subscribers)
    else:
        schedule.every().day.at("06:10:00").do(_notify_subscribers)

    try:
        _SUBSCRIBERS = pickle.load(open(_PICKLE_FILENAME, 'rb'))
    except:
        pass

    _SEND_MESSAGE_FUNC = send_message_func


def add_subscriber(tg_id: int):
    global _SUBSCRIBERS

    if id not in _SUBSCRIBERS:
        _SUBSCRIBERS.add(tg_id)

    pickle.dump(_SUBSCRIBERS, open(_PICKLE_FILENAME, 'wb'))


def _notify_subscribers():
    logging.getLogger(__name__).info('Notify subscribers')

    if not _SEND_MESSAGE_FUNC:
        logging.getLogger(__name__).error('Failed to notify subscribers because ')
        return

    # use try/except because if something goes wrong inside, the scheduler will
    # not emit the event next time
    try:
        msg = get_upcoming_matches_str()
        for subscriber_id in _SUBSCRIBERS:
            try:
                _SEND_MESSAGE_FUNC(subscriber_id, msg)
            except Exception as ex:
                logging.error(f'Exception while notifying subscriber (id={subscriber_id}): {ex}')
    except Exception as ex:
        logging.error(f'Exception while getting upcoming matches text: {ex}')
