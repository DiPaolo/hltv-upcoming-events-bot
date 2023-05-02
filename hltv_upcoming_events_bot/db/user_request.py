import datetime
import logging
from typing import Optional, List

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, BigInteger, desc
from sqlalchemy.orm import Session

from hltv_upcoming_events_bot import domain
from hltv_upcoming_events_bot.db import get_chat, get_user
from hltv_upcoming_events_bot.db.common import Base


class UserRequest(Base):
    __tablename__ = "user_request"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chat.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    utc_time = Column(DateTime)
    telegram_utc_time = Column(DateTime)
    telegram_message_id = Column(BigInteger)
    text = Column(String)

    def __repr__(self):
        return f"UserRequest(id={self.id!r})"

    def to_domain_object(self, session: Session):
        chat = get_chat(self.chat_id, session)
        user = get_user(self.user_id, session)

        return domain.user_request.UserRequest(chat=chat.to_domain_object(), user=user.to_domain_object(),
                                               utc_time=self.utc_time, telegram_utc_time=self.telegram_utc_time,
                                               telegram_message_id=self.telegram_message_id, text=self.text)


def add_user_request(chat_id: Integer, user_id: Integer, utc_time: datetime.datetime,
                     telegram_utc_time: datetime.datetime, telegram_message_id: int, text: str,
                     session: Session) -> Optional[Integer]:
    user_request = UserRequest(chat_id=chat_id, user_id=user_id, utc_time=utc_time, telegram_utc_time=telegram_utc_time,
                               telegram_message_id=telegram_message_id, text=text)

    try:
        session.add(user_request)
        session.commit()
        logging.info(
            f"User request added: chat (id={chat_id}), user (id={user_id}), utc_time={utc_time}, "
            f"telegram_utc_time={telegram_utc_time}, telegram_message_id={telegram_message_id}, {text}")
    except Exception as e:
        logging.error(f"failed to add user request (chat_id={chat_id}, user_id={user_id}): {e}")

    return user_request.id


def get_recent_user_requests(n: int, session: Session) -> List[UserRequest]:
    return session.query(UserRequest).order_by(desc('utc_time')).limit(n)
