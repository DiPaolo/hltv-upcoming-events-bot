import datetime
import logging
import sys
from typing import Optional, Dict

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, BigInteger
from sqlalchemy.orm import relationship, Session

import domain.match
from db.common import Base, get_engine
from db.match_stars import MatchStars
from db.team import Team, get_team_by_name, add_team, get_team


class Match(Base):
    __tablename__ = "match"
    id = Column(Integer, primary_key=True)
    unix_time_utc_sec = Column(BigInteger, nullable=False)
    team1_id = Column(Integer, ForeignKey("team.id"))
    # team1 = relationship("Team", back_populates="children")
    team2_id = Column(Integer, ForeignKey("team.id"))
    # team2 = relationship("Team", back_populates="children")
    stars = Column(Enum(MatchStars))
    url = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"Match(id={self.id!r})"

    # def to_domain_object(self):
    #     return domain.match.Match()


def add_match_from_domain_object(match: domain.match.Match, session: Session = None) -> Optional[Match]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    team1 = Team.from_domain_object(match.team1)
    if team1:
        team1_id = team1.id
    else:
        team1_id = add_team(match.team1.name, match.team1.url)

    team2 = Team.from_domain_object(match.team2)
    if team2:
        team2_id = team2.id
    else:
        team2_id = add_team(match.team2.name, match.team2.url)

    return add_match(team1_id, team2_id,
                     int(datetime.datetime.timestamp(match.time_utc)), MatchStars.from_domain_object(match.stars),
                     match.url)


def add_match(team1_id: Integer, team2_id: Integer, unix_time_sec: int, match_stars: MatchStars, url: str,
              session: Session = None) -> Optional[Integer]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    # if team1 is None or team2 is None:
    #     logging.error(f'failed to add match because team1 (={team1}) or team2 (={team2}) is None')
    #     return None

    team1 = get_team(team1_id)
    if team1 is None:
        logging.error(f'failed to add match because team1 (id={team1_id}) is not found')
        return None

    team2 = get_team(team2_id)
    if team2 is None:
        logging.error(f'failed to add match because team2 (id={team2_id}) is not found')
        return None

    match = Match(unix_time_utc_sec=unix_time_sec, team1_id=team1_id, team2_id=team2_id, stars=match_stars, url=url)
    cur_session.add(match)

    # created at the beginning of the function
    if not session:
        try:
            cur_session.commit()
            logging.info(
                f"Match added: team1 (id={team1.id}, name={team1.name}) vs team2 (id={team2.id}, name={team2.name}) "
                f"at {str(datetime.datetime.fromtimestamp(match.unix_time_utc_sec))}")
        except Exception as e:
            print(f"ERROR failed to add match between team1 (id={team1_id}) and team2 (id={team2_id}) at "
                  f"{datetime.datetime.fromtimestamp(unix_time_sec)}: {e}")

    return match.id


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
