import datetime
import logging
from typing import Optional, List

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, BigInteger, desc
from sqlalchemy.orm import Session

from hltv_upcoming_events_bot.db.common import Base, get_engine
from hltv_upcoming_events_bot.db.user import get_user


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


def add_user_request(chat_id: Integer, user_id: Integer, utc_time: datetime.datetime,
                     telegram_utc_time: datetime.datetime, telegram_message_id: int, text: str,
                     session: Session = None) -> Optional[Integer]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    # user = get_user(user_id)
    # if user is None:
    #     logging.error(f'failed to add user reqeust because user (id={user_id}) is not found')
    #     return None

    user_request = UserRequest(chat_id=chat_id, user_id=user_id, utc_time=utc_time, telegram_utc_time=telegram_utc_time,
                               telegram_message_id=telegram_message_id, text=text)

    try:
        cur_session.add(user_request)
        cur_session.commit()
        logging.info(
            f"User request added: chat (id={chat_id}), user (id={user_id}), utc_time={utc_time}, "
            f"telegram_utc_time={telegram_utc_time}, telegram_message_id={telegram_message_id}, {text}")
    except Exception as e:
        logging.error(f"failed to add user request (chat_id={chat_id}, user_id={user_id}): {e}")

    return user_request.id


def get_recent_user_requests(n: int = 10, session: Session = None) -> List[UserRequest]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return list()

    ret = cur_session.query(UserRequest).order_by(desc('utc_time')).limit(n)
    return ret
