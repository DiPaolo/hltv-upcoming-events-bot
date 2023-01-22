import datetime
import sys
from typing import Optional, Dict

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, BigInteger
from sqlalchemy.orm import relationship, Session

import domain.match
from db.common import Base, get_engine
from db.match_stars import MatchStars
from db.team import Team


class Match(Base):
    __tablename__ = "match"
    id = Column(Integer, primary_key=True)
    unix_time_utc_sec = Column(BigInteger, nullable=False)
    team1_id = Column(Integer, ForeignKey("team.id"))
    # team1 = relationship("Team", back_populates="children")
    team2_id = Column(Integer, ForeignKey("team.id"))
    # team2 = relationship("Team", back_populates="children")
    stars = Column(Enum(MatchStars), default=MatchStars.ZERO)
    url = Column(String)

    def __repr__(self):
        return f"Match(id={self.id!r}"

    # def to_domain_object(self):
    #     return domain.match.Match()


def add_match(team1: Team, team2: Team, unix_time_sec: int, stars: MatchStars, url: str, session: Session = None):
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    match = Match(unix_time_utc_sec=unix_time_sec, team1_id=team1.id, team2_id=team2.id, stars=stars, url=url)
    cur_session.add(match)

    # created at the beginning of the function
    if not session:
        try:
            cur_session.commit()
        except Exception as e:
            print(f"ERROR failed to add match between '{team1.name}' and '{team2.name}' at "
                  f"{datetime.datetime.fromtimestamp(unix_time_sec)}: {e}")


def get_match(match_id: Integer, session: Session = None) -> Optional[Match]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    ret = cur_session.get(Match, match_id)

    # created at the beginning of the function
    if not session:
        cur_session.commit()

    return ret


def update_match(match_id: Integer, props: Dict, session: Session = None):
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    skin = get_match(match_id, cur_session)
    for key, value in props.items():
        setattr(skin, key, value)

    # created at the beginning of the function
    if not session:
        cur_session.commit()
