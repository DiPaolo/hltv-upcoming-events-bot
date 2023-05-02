import logging
from typing import Optional, List

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import Session

from hltv_upcoming_events_bot import domain
from hltv_upcoming_events_bot.db import RetCode
from hltv_upcoming_events_bot.db.common import Base
from hltv_upcoming_events_bot.db.chat import add_chat_from_domain_object, get_chat_by_telegram_id, Chat


class Subscriber(Base):
    __tablename__ = "subscriber"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    chat_id = Column(Integer, ForeignKey("chat.id"))

    def __repr__(self):
        return f"Subscriber(id={self.id!r})"

    # def to_domain_object(self):
    #     return domain.team.Team(name=self.name, url=self.url)


def add_subscriber_from_domain_object(chat: domain.Chat, session: Session) -> Optional[Subscriber]:
    db_chat = get_chat_by_telegram_id(chat.telegram_id, session)
    if db_chat is None:
        db_chat = add_chat_from_domain_object(chat, session)
        session.flush()
        if db_chat is None:
            logging.error(
                f'failed to subscribe user/chat (telegram_id={chat.telegram_id}, title={chat.title}): '
                f'failed to create user object in DB')
            return None

    subscriber = Subscriber(chat_id=db_chat.id)
    session.add(subscriber)
    session.commit()

    return subscriber


def delete_subscriber_by_id(subscriber_id: Integer, session: Session) -> RetCode:
    db_subs = get_subscriber(subscriber_id, session)
    if db_subs is None:
        logging.error(
            f'failed to unsubscribe user/chat (id={subscriber_id}): no such subscriber in DB')
        return RetCode.NOT_EXIST

    try:
        session.delete(db_subs)
        session.commit()
        return RetCode.OK
    except Exception as ex:
        logging.error(f'failed to delete subscriber by ID (id={subscriber_id}): {ex}')
        return RetCode.ERROR


def get_subscribers(session: Session) -> List[Subscriber]:
    return session.query(Subscriber).all()


def get_subscriber(subscriber_id: Integer, session: Session) -> Optional[Subscriber]:
    return session.get(Subscriber, subscriber_id)


def get_subscriber_by_telegram_id(telegram_id: int, session: Session) -> Optional[Subscriber]:
    return session \
        .query(Subscriber) \
        .join(Chat) \
        .filter(Chat.telegram_id == telegram_id) \
        .first()
