import logging
from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

import hltv_upcoming_events_bot.domain as domain
from hltv_upcoming_events_bot.db.common import Base


class MatchState(Base):
    __tablename__ = "match_state"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"MatchState(id={self.id!r}, name={self.name!r})"

    @staticmethod
    def from_domain_object(domain_obj: domain.MatchState):
        return domain.MatchState(domain_obj.value)

    def to_domain_object(self):
        return domain.MatchState(domain.get_match_state_by_name(self.name))


# def add_match_state_from_domain_object(match_state: domain.match_state.MatchState, session: Session = None) -> Optional[Integer]:
#     return add_match_state(match_state.name, session)


def add_match_state(name: str, session: Session) -> Optional[Integer]:
    match_state = get_match_state_by_name(name, session)
    if match_state:
        return match_state.id

    match_state = MatchState(name=name)
    session.add(match_state)

    # created at the beginning of the function
    try:
        session.commit()
        logging.info(f"Match state added (id={match_state.id}, name={match_state.name})")
    except Exception as e:
        logging.error(f"Failed to add match state '{name}': {e}")

    return match_state.id


def get_match_state(match_state_id: Integer, session: Session) -> Optional[MatchState]:
    return session.get(MatchState, match_state_id)


def get_match_state_by_name(name: str, session: Session) -> Optional[MatchState]:
    try:
        return session.query(MatchState).filter(MatchState.name == name).first()
    except BaseException as e:
        logging.error(f"Failed to get match state (name={name}) from DB: {e}")
        return None
