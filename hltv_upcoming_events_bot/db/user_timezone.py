import logging
from typing import Optional, List

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import Session

from hltv_upcoming_events_bot import domain
from hltv_upcoming_events_bot.db.common import Base
from hltv_upcoming_events_bot.db.user import add_user_from_domain_object, get_user_by_telegram_id


class UserTimezone(Base):
    __tablename__ = "user_timezone"
    id = Column(Integer, primary_key=True)
    utc_offset_minutes = Column(Integer)
    user_id = Column(Integer, ForeignKey("user.id"))

    def __repr__(self):
        return f"UserTimezone(id={self.id!r})"

    # def to_domain_object(self):
    #     return domain.team.Team(name=self.name, url=self.url)


def add_user_timezone(tg_id: int, utc_offset_minutes: int, session: Session = None) -> Optional[UserTimezone]:
    if not -12 <= utc_offset_minutes // 60 <= 14:
        logging.error(
            f'Failed to set timezone for user (telegram_id={tg_id}, utc_offset_minutes={utc_offset_minutes}): '
            f'value is out of valid range')
        return None

    user = get_user_by_telegram_id(tg_id, session)
    if user is None:
        logging.error(
            f'Failed to set timezone for user (telegram_id={tg_id}, utc_offset_minutes={utc_offset_minutes}): '
            f'user is not found')
        return None

    user_timezone = UserTimezone(utc_offset_minutes=utc_offset_minutes, user_id=user.id)
    try:
        session.add(user_timezone)
        session.commit()
    except Exception as ex:
        logging.error(
            f'Failed to set timezone for user (telegram_id={tg_id}, utc_offset_minutes={utc_offset_minutes}): {ex}')
        return None

    return user_timezone


def delete_subscriber_by_id(subscriber_id: Integer, session: Session):
    db_subs = get_subscriber(subscriber_id, session)
    if db_subs is None:
        logging.error(
            f'Failed to unsubscribe user (id={subscriber_id}): no such subscriber in DB')
        return

    session.delete(db_subs)
    session.commit()


def get_user_timezone(tg_id: int, session: Session) -> List[UserTimezone]:
    return session.query(UserTimezone)\
        .filter(UserTimezone.user ==)\
        .first()


def get_subscriber(subscriber_id: Integer, session: Session) -> Optional[Subscriber]:
    return session.get(Subscriber, subscriber_id)
