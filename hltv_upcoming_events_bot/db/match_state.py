import logging
from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

import hltv_upcoming_events_bot.domain.match_state
from hltv_upcoming_events_bot.db.common import Base, get_engine


class MatchState(Base):
    __tablename__ = "match_state"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"MatchState(id={self.id!r}, name={self.name!r})"

    @staticmethod
    def from_domain_object(domain_obj: hltv_upcoming_events_bot.domain.match_state.MatchState):
        return hltv_upcoming_events_bot.domain.match_state.MatchState(domain_obj.value)


def add_match_state_from_domain_object(match_state: hltv_upcoming_events_bot.domain.match_state.MatchState, session: Session = None) -> Optional[Integer]:
    return add_match_state(match_state.name, session)


def add_match_state(name: str, session: Session = None) -> Optional[Integer]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    match_state = get_match_state_by_name(name, cur_session)
    if match_state:
        return match_state.id

    match_state = MatchState(name=name)
    cur_session.add(match_state)

    # created at the beginning of the function
    if not session:
        try:
            cur_session.commit()
            logging.info(f"Match state added (id={match_state.id}, name={match_state.name})")
        except Exception as e:
            print(f"ERROR failed to add match state '{name}': {e}")

    return match_state.id


def get_match_state_by_name(name: str, session: Session = None) -> Optional[MatchState]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    try:
        match_state = cur_session.query(MatchState).filter(MatchState.name == name).first()
    except BaseException as e:
        logging.error(f"failed to get match state (name={name}) from DB: {e}")
        return None

    return match_state