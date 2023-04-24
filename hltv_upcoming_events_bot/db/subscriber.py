import datetime
import logging
from typing import Optional, Dict

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, BigInteger
from sqlalchemy.orm import Session

import hltv_upcoming_events_bot.domain.match
from hltv_upcoming_events_bot.db.common import Base, get_engine
from hltv_upcoming_events_bot.db.match_stars import MatchStars
from hltv_upcoming_events_bot.db.team import Team, add_team, get_team
from hltv_upcoming_events_bot.domain import get_match_state_name


class Subscriber(Base):
    __tablename__ = "subscriber"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    telegram_id = Column
    unix_time_utc_sec = Column(BigInteger, nullable=False)
    team1_id = Column(Integer, ForeignKey("team.id"))
    team2_id = Column(Integer, ForeignKey("team.id"))
    stars = Column(Enum(MatchStars))
    state_id = Column(Integer, ForeignKey("match_state.id"))
    tournament_id = Column(Integer, ForeignKey('tournament.id'))
    url = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"Match(id={self.id!r})"

    # def to_domain_object(self):
    #     return domain.match.Match()


def add_match_from_domain_object(match: hltv_upcoming_events_bot.domain.match.Match, session: Session = None) -> Optional[Match]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    team1 = Team.from_domain_object(match.team1)
    team1_id = team1.id if team1 else add_team(match.team1.name, match.team1.url)

    team2 = Team.from_domain_object(match.team2)
    team2_id = team2.id if team2 else add_team(match.team2.name, match.team2.url)

    state_name = get_match_state_name(match.state)
    state = hltv_upcoming_events_bot.db.match_state.get_match_state_by_name(state_name)
    state_id = state.id if state else hltv_upcoming_events_bot.db.match_state.add_match_state(state_name)

    tournament = hltv_upcoming_events_bot.db.tournament.get_tournament_id_by_name(match.tournament.name)
    if tournament is None:
        tournament = hltv_upcoming_events_bot.db.tournament.add_tournament_from_domain_object(match.tournament)
        if tournament is None:
            tournament = hltv_upcoming_events_bot.db.tournament.get_unknown_tournament_id()
            if tournament is None:
                logging.error(
                    f'failed to add match from domain object: failed to found tournament (name={match.tournament.name})')
                return None

    return add_match(team1_id, team2_id,
                     int(datetime.datetime.timestamp(match.time_utc)), MatchStars.from_domain_object(match.stars),
                     tournament.id, state_id, match.url)


def add_match(team1_id: Integer, team2_id: Integer, unix_time_sec: int, match_stars: MatchStars, tournament_id: Integer,
              state_id: Integer, url: str,
              session: Session = None) -> Optional[Integer]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    team1 = get_team(team1_id)
    if team1 is None:
        logging.error(f'failed to add match because team1 (id={team1_id}) is not found')
        return None

    team2 = get_team(team2_id)
    if team2 is None:
        logging.error(f'failed to add match because team2 (id={team2_id}) is not found')
        return None

    match = Match(unix_time_utc_sec=unix_time_sec, team1_id=team1_id, team2_id=team2_id, stars=match_stars,
                  state_id=state_id, url=url)
    cur_session.add(match)

    # created at the beginning of the function
    if not session:
        try:
            cur_session.commit()
            logging.info(
                f"Match added: team1 (id={team1.id}, name={team1.name}) vs team2 (id={team2.id}, name={team2.name}) "
                f"with the status (id={state_id}) at {str(datetime.datetime.fromtimestamp(match.unix_time_utc_sec))}")
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
