import logging
from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session

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


# def get_recent_user_request(max_count: int) -> List[domain.UserRequest]:
#     out = list()
#     with Session(get_engine()) as session:
#         requests = db.get_recent_user_requests(max_count, session)
#         for req in requests:
#             # TODO add mapping
#             match_translations = db.get_translations_by_match_id(match.id, session)
#             domain_match = None
#             for trans in match_translations:
#                 if domain_match is None:
#                     domain_match = match.to_domain_object(session)
#
#                 streamer = db.get_streamer(trans.streamer_id, session)
#                 domain_streamer = streamer.to_domain_object()
#                 out.append(domain.Translation(domain_match, domain_streamer))
#
#     return out
