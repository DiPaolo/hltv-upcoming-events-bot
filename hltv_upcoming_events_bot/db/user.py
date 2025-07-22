import logging
from typing import Optional, List

from sqlalchemy import Boolean, Column, Integer, String, BigInteger
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from hltv_upcoming_events_bot import domain
from hltv_upcoming_events_bot.db.common import Base

_logger = logging.getLogger('hltv_upcoming_events_bot.db')


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_bot = Column(Boolean)
    is_premium = Column(Boolean)
    language_code = Column(String)

    def __repr__(self):
        return f"User(id={self.id!r})"

    def to_domain_object(self):
        return domain.user.User(telegram_id=self.telegram_id, username=self.username, first_name=self.first_name,
                                last_name=self.last_name, is_bot=self.is_bot, is_premium=self.is_premium,
                                language_code=self.language_code)


def add_user_from_domain_object(user: domain.User, session: Session) -> Optional[Integer]:
    return add_user(user.telegram_id, user.username, user.first_name, user.last_name, user.is_bot, user.is_premium,
                    user.language_code, session)


def add_user(telegram_id: int, username: str, first_name: str, last_name: str, is_bot: bool, is_premium: bool,
             language_code: str, session: Session) -> Optional[Integer]:
    match = User(telegram_id=telegram_id, username=username, first_name=first_name, last_name=last_name, is_bot=is_bot,
                 is_premium=is_premium, language_code=language_code)

    try:
        session.add(match)
        session.commit()
        _logger.info(f"User added (id={match.id}, username={match.username}, telegram_id={match.telegram_id})")
    except Exception as e:
        print(f"ERROR failed to add user (username={username}, telegram_id={telegram_id}): {e}")

    return match.id


def get_user(user_id: Integer, session: Session) -> Optional[User]:
    return session.get(User, user_id)


# def get_user_by_telegram_id(telegram_id: int, session: Session = None) -> Optional[User]:
#     cur_session = session if session else Session(get_engine())
#     if cur_session is None:
#         return None


def get_user_by_telegram_id(telegram_id: int, session: Session) -> Optional[User]:
    try:
        return session.query(User).filter(User.telegram_id == telegram_id).one()
    except NoResultFound:
        return None


def get_users(session: Session) -> List[User]:
    return session.query(User).all()

# def update_user(user_id: Integer, props: Dict, session: Session):
#     skin = get_user(user_id, session)
#     for key, value in props.items():
#         setattr(skin, key, value)
#
#     session.commit()
