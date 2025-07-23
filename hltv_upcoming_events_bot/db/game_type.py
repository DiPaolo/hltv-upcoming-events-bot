import logging
from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

import hltv_upcoming_events_bot.domain as domain
from hltv_upcoming_events_bot.db.common import Base

_logger = logging.getLogger('hltv_upcoming_events_bot.db')


class GameType(Base):
    __tablename__ = "game_type"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"GameType(id={self.id!r}, name={self.name!r})"

    @staticmethod
    def from_domain_object(domain_obj: domain.GameType):
        return domain.GameType(domain_obj.value)

    # def to_domain_object(self):
    #     return domain.GameType(domain.get_game_type_by_name(self.name))


# def add_game_type(name: str, session: Session) -> Optional[Integer]:
#     match_state = get_match_state_by_name(name, session)
#     if match_state:
#         return match_state.id
#
#     match_state = MatchState(name=name)
#     session.add(match_state)
#
#     # created at the beginning of the function
#     try:
#         session.commit()
#         _logger.info(f"Match state added (id={match_state.id}, name={match_state.name})")
#     except Exception as e:
#         _logger.error(f"Failed to add match state '{name}': {e}")
#
#     return match_state.id


def get_game_type(game_type_id: Integer, session: Session) -> Optional[GameType]:
    return session.get(GameType, game_type_id)


def get_game_type_by_name(name: str, session: Session) -> Optional[GameType]:
    try:
        return session.query(GameType).filter(GameType.name == name).first()
    except BaseException as e:
        _logger.error(f"Failed to get game type by name (name={name}) from DB: {e}")
        return None
