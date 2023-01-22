import sys
from typing import Optional, Dict

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, BigInteger
from sqlalchemy.orm import relationship, Session

from db.common import Base, get_engine


class Team(Base):
    __tablename__ = "team"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    url = Column(String)

    def __repr__(self):
        return f"Team(id={self.id!r}, name={self.name!r})"

    # def to_domain_object(self):
    #     return domain.team.Team()


def add_team(name: str, url: str, session: Session = None) -> Optional[Team]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    team = get_team_by_name(name)
    if team:
        return team

    team = Team(name=name, url=url)
    cur_session.add(team)

    # created at the beginning of the function
    if not session:
        try:
            cur_session.commit()
        except Exception as e:
            print(f"ERROR failed to add team '{name}': {e}")

    return team


def get_team(team_id: Integer, session: Session = None) -> Optional[Team]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    ret = cur_session.get(Team, team_id)

    # created at the beginning of the function
    if not session:
        cur_session.commit()

    return ret


def get_team_by_name(name: str, session: Session = None) -> Optional[Team]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    team = cur_session.query(Team).filter(Team.name == name).first()

    # created at the beginning of the function
    # if not session:
    #     cur_session.commit()

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
