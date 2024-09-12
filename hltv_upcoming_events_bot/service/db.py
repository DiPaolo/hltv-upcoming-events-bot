import datetime
import logging
from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session, sessionmaker

from hltv_upcoming_events_bot import db
from hltv_upcoming_events_bot import domain
from hltv_upcoming_events_bot.db import RetCode
from hltv_upcoming_events_bot.db.common import get_engine


def add_match(match: domain.Match):
    with Session(get_engine()) as session:
        db.add_match_from_domain_object(match, session)


def add_streamer(streamer: domain.Streamer):
    with Session(get_engine()) as session:
        db.add_streamer_from_domain_object(streamer, session)


def add_translation(match: domain.Match, streamer: domain.Streamer):
    with Session(get_engine()) as session:
        match_id = db.get_match_id_by_url(match.url, session)
        if match_id is None:
            match = db.add_match_from_domain_object(match, session)
            match_id = match.id
            if match_id is None:
                raise Exception(
                    f'Failed to add translation (match_url={match.url}, streamer_name={streamer.name}, '
                    f'streamer_url={streamer.url}): Failed to get match ID (match_url={match.url})')

        streamer_id = db.get_streamer_id_by_url(streamer.url, session)
        if streamer_id is None:
            streamer = db.add_streamer_from_domain_object(streamer, session)
            streamer_id = streamer.id
            if streamer_id is None:
                raise Exception(
                    f'Failed to add translation (match_url={match.url}, streamer_name={streamer.name}, '
                    f'streamer_url={streamer.url}): Failed to get streamer ID (streamer_url={streamer.url})')

        db.add_translation(match_id, streamer_id, session)


def subscribe_chat_by_telegram_id(tg_id: int) -> RetCode:
    with Session(get_engine()) as session:
        subs = db.get_subscriber_by_telegram_id(tg_id, session)
        if subs is not None:
            return RetCode.ALREADY_EXIST

        chat = db.get_chat_by_telegram_id(tg_id, session)
        if chat is None:
            logging.error(f'failed to subscribe user/chat: no such chat (telegram_id={tg_id}) in DB')
            return RetCode.ERROR

        ret = db.add_subscriber_from_domain_object(chat, session)
        if ret is None:
            return RetCode.ERROR

        return RetCode.OK


def unsubscribe_chat_by_telegram_id(tg_id) -> RetCode:
    with Session(get_engine()) as session:
        db_subscriber = db.get_subscriber_by_telegram_id(tg_id, session)
        if db_subscriber is None:
            return RetCode.NOT_EXIST

        return db.delete_subscriber_by_id(db_subscriber.id, session)


def get_users() -> List[domain.User]:
    out = list()

    with Session(get_engine()) as session:
        db_users = db.get_users(session)
        for db_user in db_users:
            out.append(db_user.to_domain_object())

    return out


def get_recent_user_requests(n: int) -> List[domain.UserRequest]:
    out = list()

    with Session(get_engine()) as session:
        db_user_requests = db.get_recent_user_requests(n, session)
        for db_user_req in db_user_requests:
            out.append(db_user_req.to_domain_object(session))

    return out


def get_subscribers() -> List[domain.User]:
    out = list()

    with Session(get_engine()) as session:
        db_subscribers = db.get_subscribers(session)
        for db_sub in db_subscribers:
            db_user = db.get_chat(db_sub.chat_id, session)
            if db_user is not None:
                out.append(db_user)

    return out


def get_translations_in_period(start_from: int, until_to: int) -> List[domain.Translation]:
    out = list()
    with Session(get_engine()) as session:
        matches = session.query(db.Match).filter(
            and_(start_from < db.Match.unix_time_utc_sec, db.Match.unix_time_utc_sec < until_to)).all()

        for match in matches:
            match_translations = db.get_translations_by_match_id(match.id, session)
            domain_match = None
            for trans in match_translations:
                if domain_match is None:
                    domain_match = match.to_domain_object(session)

                streamer = db.get_streamer(trans.streamer_id, session)
                domain_streamer = streamer.to_domain_object()
                out.append(domain.Translation(domain_match, domain_streamer))

    return out


def add_news_item(news_item_domain: domain.NewsItem) -> RetCode:
    with Session(get_engine()) as session:
        return _add_news_item_with_session(news_item_domain, session)


def add_news_items(news_items_domain: List[domain.NewsItem]) -> RetCode:
    with Session(get_engine()) as session:
        added_msgs = list()
        updated_msgs = list()
        failed_msgs = list()
        for news_item_domain in news_items_domain:
            ret = _add_news_item_with_session(news_item_domain, session)
            msg = f'    {news_item_domain.date_time_utc}, {news_item_domain.title}'
            if ret == RetCode.OK:
                added_msgs.append(msg)
            elif ret == RetCode.ALREADY_EXIST:
                ret = _update_news_item_with_session(news_item_domain, session)
                if ret == RetCode.OK:
                    updated_msgs.append(msg)
                else:
                    failed_msgs.append(msg)
            else:
                failed_msgs.append(msg)

        session.commit()

        logging.info(f"{len(added_msgs)} news item(s) added{':' if len(added_msgs) > 0 else ''}")
        for msg in added_msgs:
            logging.info(f'    {msg}')

        logging.info(f"{len(updated_msgs)} news item(s) updated{':' if len(updated_msgs) > 0 else ''}")
        for msg in updated_msgs:
            logging.info(f'    {msg}')

        logging.info(f"{len(failed_msgs)} news item(s) failed to add{':' if len(failed_msgs) > 0 else ''}")
        for msg in failed_msgs:
            logging.info(f'    {msg}')

        return RetCode.OK


def _add_news_item_with_session(news_item_domain: domain.NewsItem, session: Session) -> RetCode:
    news_item = db.get_news_item_by_url(news_item_domain.url, session)
    if news_item is not None:
        return RetCode.ALREADY_EXIST

    news_item = db.add_news_item_from_domain_object(news_item_domain, session)
    if news_item is None:
        return RetCode.ERROR

    return RetCode.OK


def update_news_item(news_item_domain: domain.NewsItem) -> RetCode:
    with Session(get_engine()) as session:
        ret = _update_news_item_with_session(news_item_domain, session)
        session.commit()
        return ret


def _update_news_item_with_session(news_item_domain: domain.NewsItem, session: Session) -> RetCode:
    news_item = db.get_news_item_by_url(news_item_domain.url, session)
    if news_item is None:
        return RetCode.NOT_EXIST

    db.update_news_item(news_item.id, news_item_domain.date_time_utc, news_item_domain.title,
                        news_item_domain.short_desc, news_item_domain.comment_count,
                        news_item_domain.comment_avg_hour, session)
    return RetCode.OK


def get_recent_news_for_chat(chat_telegram_id: int, since_time_utc: datetime.datetime, max_count: int = None, db_engine = None) -> \
        List[domain.NewsItem]:
    out = list()

    session_maker = sessionmaker(db_engine if db_engine else get_engine())

    with session_maker() as session:
        chat = db.get_chat_by_telegram_id(chat_telegram_id, session)
        if chat is None:
            logging.error(f'failed to get recent news items for chat (telegram_id={chat_telegram_id}')
            return out

        news_items = db.get_recent_news_items_for_chat(chat.id, since_time_utc,
                                                       max_count if max_count is not None else 20, session)
        for news_item in news_items:
            out.append(news_item.to_domain_object())

    return out


def mark_news_items_as_sent(news_items_domain: List[domain.NewsItem], sent_telegram_id_list: List[int], db_engine = None):
    session_maker = sessionmaker(db_engine if db_engine else get_engine())

    with session_maker() as session:
        for news_item_domain in news_items_domain:
            news_item = db.get_news_item_by_url(news_item_domain.url, session)
            if news_item is None:
                logging.error(f'failed to mark news item as sent: no such news item (title={news_item_domain.title}, '
                              f'url={news_item_domain.url})')
                return

            for sent_telegram_id in sent_telegram_id_list:
                chat = db.get_chat_by_telegram_id(sent_telegram_id, session)
                if chat is None:
                    logging.error(f'failed to mark news item as sent for chat (telegram_id={sent_telegram_id}): '
                                  f'no such chat')
                    continue

                # add if not added
                if len(db.get_news_item_sent_by_news_item_id_and_chat_id(news_item.id, chat.id, session)) == 0:
                    db.add_news_item_sent(news_item.id, chat.id, session)
