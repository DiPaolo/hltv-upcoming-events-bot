import datetime
import logging
from enum import Enum
from typing import Optional, List

import hltv_upcoming_events_bot.service.db as db_service
from hltv_upcoming_events_bot import domain
from hltv_upcoming_events_bot.service import cybersport_parser as parser

_CACHED_MATCHES: Optional[List] = None


class RetCode(Enum):
    OK = 1
    ERROR = 2
    NOT_EXIST = 3
    ALREADY_EXIST = 4

    @staticmethod
    def map_from_db(db_ret_code: db_service.RetCode):
        if db_ret_code == db_service.RetCode.OK:
            return RetCode.OK
        elif db_ret_code == db_service.RetCode.ERROR:
            return RetCode.ERROR
        elif db_ret_code == db_service.RetCode.ALREADY_EXIST:
            return RetCode.ALREADY_EXIST
        else:
            logging.error(f'unhandled value returned from database service ({db_ret_code})')
            return RetCode.ERROR


def start():
    pass
    # _setup_schedule()


def get_recent_news_str(news_items: List[domain.NewsItem]) -> str:
    news_item_str_list = list()
    for news_item in news_items:
        match_str = f"<b><a href='{news_item.url}'>{news_item.title}</a></b>\n\n" \
                    f"{news_item.short_desc}"
        news_item_str_list.append(match_str)

    msg = '\n\n'.join(news_item_str_list)
    return 'никаких интересных новостей за последнее время :(' if not msg else msg


def get_recent_news_for_chat(chat_telegram_id: int, since_time_utc: datetime.datetime, max_count: int = None) -> List[
    domain.NewsItem]:
    logging.info(f'Get recent news for chat (chat_telegram_id={chat_telegram_id}, since_time_utc={since_time_utc}, '
                 f'max={max_count})')
    return db_service.get_recent_news_for_chat(chat_telegram_id, since_time_utc, max_count)


def populate_news(to_date_time: datetime.datetime = None):
    logging.info(f"Populate news until '{to_date_time}'")
    _add_news_to_db(_parse_news(to_date_time))


# def _setup_schedule():
#     if config.DEBUG:
#         schedule.every(3).minutes.do(populate_vacancies)
#     else:
#         schedule.every(4).to(6).hours.do(populate_vacancies)
#
#     # initial call
#     populate_vacancies()


def _parse_news(to_date_time: datetime.datetime = None) -> List[domain.NewsItem]:
    # use try/except because if something goes wrong inside, the scheduler will
    # not emit the event next time

    news = list()
    try:
        news = parser.parse_news_to_date(to_date_time)
    except Exception as ex:
        logging.error(f'failed to parse news: {ex}')

    return news


def _add_news_to_db(news: List[domain.NewsItem]):
    for news_item in news:
        ret = db_service.add_news_item(news_item)
        if RetCode.map_from_db(ret) == RetCode.ALREADY_EXIST:
            db_service.update_news_item(news_item)
