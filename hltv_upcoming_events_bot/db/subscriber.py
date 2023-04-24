import logging
from typing import Optional, List

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import Session

from hltv_upcoming_events_bot import domain
from hltv_upcoming_events_bot.db.common import Base
from hltv_upcoming_events_bot.db.user import add_user_from_domain_object, get_user_by_telegram_id


class Subscriber(Base):
    __tablename__ = "subscriber"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))

    def __repr__(self):
        return f"Subscriber(id={self.id!r})"

    def to_domain_object(self):
        return domain.team.Team(name=self.name, url=self.url)


def add_subscriber_from_domain_object(user: domain.User, session: Session = None) -> Optional[Subscriber]:
    db_user = get_user_by_telegram_id(user.telegram_id, session)
    if db_user is None:
        db_user = add_user_from_domain_object(user, session)
        session.flush()
        if db_user is None:
            logging.error(
                f'Failed to subscribe user (username={user.username}, telegram_id={user.telegram_id}): failed to '
                f'create user object in DB')
            return None

    subscriber = Subscriber(user_id=db_user.id)
    session.add(subscriber)
    session.commit()

    return subscriber


def delete_subscriber_by_id(subscriber_id: Integer, session: Session):
    db_subs = get_subscriber(subscriber_id, session)
    if db_subs is None:
        logging.error(
            f'Failed to unsubscribe user (id={subscriber_id}): no such subscriber in DB')
        return

    session.delete(db_subs)
    session.commit()


def get_subscribers(session: Session) -> List[Subscriber]:
    return session.query(Subscriber).all()


def get_subscriber(subscriber_id: Integer, session: Session) -> Optional[Subscriber]:
    return session.get(Subscriber, subscriber_id)
