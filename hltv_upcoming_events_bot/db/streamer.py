import logging
from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

import hltv_upcoming_events_bot.domain as domain
from hltv_upcoming_events_bot.db.common import Base

_logger = logging.getLogger('hltv_upcoming_events_bot.db')


class Streamer(Base):
    __tablename__ = "streamer"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    language = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"Streamer(id={self.id!r}, name={self.name!r}, language={self.language!r})"

    def to_domain_object(self):
        return domain.Streamer(name=self.name, language=self.language, url=self.url)


def add_streamer_from_domain_object(streamer: domain.Streamer, session: Session) -> Optional[Streamer]:
    return add_streamer(streamer.name, streamer.language, streamer.url, session)


def add_streamer(name: str, language: str, url: str, session: Session) -> Optional[Integer]:
    streamer_id = get_streamer_id_by_url(url, session)
    if streamer_id:
        return streamer_id

    streamer = Streamer(name=name, language=language, url=url)
    session.add(streamer)

    try:
        session.commit()
        _logger.info(f"Streamer added (id={streamer.id}, name={streamer.name}, lang={streamer.language})")
        return streamer
    except Exception as e:
        _logger.error(f"Failed to add streamer '{name}' with language '{language}': {e}")
        return None


def get_streamer(streamer_id: Integer, session: Session) -> Optional[Streamer]:
    return session.get(Streamer, streamer_id)


def get_streamer_by_url(url: str, session: Session) -> Optional[Streamer]:
    return session.query(Streamer).filter(Streamer.url == url).first()


def get_streamer_id_by_url(url: str, session: Session) -> Optional[Integer]:
    streamer = session.query(Streamer).filter(Streamer.url == url).first()
    if streamer is None:
        return None
    return streamer.id
