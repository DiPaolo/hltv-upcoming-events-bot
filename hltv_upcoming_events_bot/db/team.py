import logging
from typing import Optional, Dict

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

import hltv_upcoming_events_bot.domain as domain
from hltv_upcoming_events_bot import domain
from hltv_upcoming_events_bot.db.common import Base, get_engine


class Team(Base):
    __tablename__ = "team"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    url = Column(String)

    def __repr__(self):
        return f"Team(id={self.id!r}, name={self.name!r})"

    @staticmethod
    def from_domain_object(team_domain: domain.Team, session: Session):
        return get_team_by_name(team_domain.name, session)

    def to_domain_object(self):
        return domain.team.Team(name=self.name, url=self.url)


def add_team_from_domain_object(team: domain.Team) -> Optional[Team]:
    return add_team(team.name, team.url)


def add_team(name: str, url: str) -> Optional[Integer]:
    with Session(get_engine()) as session:
        team = get_team_by_name(name, session)
        if team:
            return team.id

        try:
            team = Team(name=name, url=url)
            session.add(team)
            session.commit()
            logging.info(f"Team added (id={team.id}, name={team.name})")
            return team.id
        except Exception as e:
            logging.error(f"Failed to add team '{name}': {e}")
            return None


def get_team(team_id: Integer, session: Session) -> Optional[Team]:
    return session.get(Team, team_id)


def get_team_by_name(name: str, session: Session) -> Optional[Team]:
    try:
        team = session.query(Team).filter(Team.name == name).first()
    except BaseException as e:
        logging.error(f"failed to get team (name={name}) from DB: {e}")
        return None

    return team


def update_team(team_id: Integer, props: Dict):
    with Session(get_engine()) as session:
        skin = get_team(team_id, session)
        for key, value in props.items():
            setattr(skin, key, value)
