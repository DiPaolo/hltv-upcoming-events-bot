import logging
from typing import Optional, Dict

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

import hltv_upcoming_events_bot.domain.team
from hltv_upcoming_events_bot.db.common import Base, get_engine


class Team(Base):
    __tablename__ = "team"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    url = Column(String)

    def __repr__(self):
        return f"Team(id={self.id!r}, name={self.name!r})"

    # def to_domain_object(self):
    #     return domain.team.Team()

    @staticmethod
    def from_domain_object(team: hltv_upcoming_events_bot.domain.team.Team, session: Session = None):
        return get_team_by_name(team.name, session)


def add_team_from_domain_object(team: hltv_upcoming_events_bot.domain.team.Team, session: Session = None) -> Optional[Team]:
    return add_team(team.name, team.url, session)


def add_team(name: str, url: str, session: Session = None) -> Optional[Integer]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    team = get_team_by_name(name, cur_session)
    if team:
        return team.id

    team = Team(name=name, url=url)
    cur_session.add(team)

    # created at the beginning of the function
    if not session:
        try:
            cur_session.commit()
            logging.info(f"Team added (id={team.id}, name={team.name})")
        except Exception as e:
            print(f"ERROR failed to add team '{name}': {e}")

    return team.id


def get_team(team_id: Integer, session: Session = None) -> Optional[Team]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    return cur_session.get(Team, team_id)


def get_team_by_name(name: str, session: Session = None) -> Optional[Team]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    try:
        team = cur_session.query(Team).filter(Team.name == name).first()
    except BaseException as e:
        logging.error(f"failed to get team (name={name}) from DB: {e}")
        return None

    return team


def update_team(team_id: Integer, props: Dict, session: Session = None):
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    skin = get_team(team_id, cur_session)
    for key, value in props.items():
        setattr(skin, key, value)

    # created at the beginning of the function
    if not session:
        cur_session.commit()
