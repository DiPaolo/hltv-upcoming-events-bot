import logging
from typing import Optional, Dict, List

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from hltv_upcoming_events_bot.db.common import Base, get_engine
from hltv_upcoming_events_bot import domain


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_bot = Column(Boolean)
    is_premium = Column(Boolean)
    language_code = Column(String)

    def __repr__(self):
        return f"User(id={self.id!r})"


def add_user_from_domain_object(user: domain.User, session: Session) -> Optional[Integer]:
    return add_user(user.telegram_id, user.username, user.first_name, user.last_name, user.is_bot, user.is_premium,
                    user.language_code, session)


def add_user(telegram_id: int, username: str, first_name: str, last_name: str, is_bot: bool, is_premium: bool,
             language_code: str, session: Session = None) -> Optional[Integer]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    match = User(telegram_id=telegram_id, username=username, first_name=first_name, last_name=last_name, is_bot=is_bot,
                 is_premium=is_premium, language_code=language_code)

    try:
        cur_session.add(match)
        cur_session.commit()
        logging.info(
            f"User added (id={match.id}, username={match.username}, telegram_id={match.telegram_id})")
    except Exception as e:
        print(f"ERROR failed to add user (username={username}, telegram_id={telegram_id}): {e}")

    return match.id


def get_user(user_id: Integer, session: Session = None) -> Optional[User]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None
    return cur_session.get(User, user_id)


def get_user_by_telegram_id(telegram_id: int, session: Session = None) -> Optional[User]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    try:
        ret = cur_session.query(User).filter(User.telegram_id == telegram_id).one()
    except NoResultFound:
        ret = None

    # # created at the beginning of the function
    # if not session:
    #     cur_session.commit()

    return ret


def get_users(session: Session = None) -> List[User]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return list()

    ret = cur_session.query(User).all()

    return ret


def update_user(user_id: Integer, props: Dict, session: Session = None):
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    skin = get_user(user_id, cur_session)
    for key, value in props.items():
        setattr(skin, key, value)

    # # created at the beginning of the function
    # if not session:
    #     cur_session.commit()
