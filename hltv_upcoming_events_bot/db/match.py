import datetime
import logging
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, BigInteger, and_
from sqlalchemy.orm import Session

import hltv_upcoming_events_bot.db as db
from hltv_upcoming_events_bot import domain
from hltv_upcoming_events_bot.db.common import Base, get_engine
from hltv_upcoming_events_bot.db.match_stars import MatchStars
from hltv_upcoming_events_bot.db.team import Team, add_team, get_team


class Match(Base):
    __tablename__ = "match"
    id = Column(Integer, primary_key=True)
    unix_time_utc_sec = Column(BigInteger, nullable=False)
    team1_id = Column(Integer, ForeignKey("team.id"))
    team2_id = Column(Integer, ForeignKey("team.id"))
    stars = Column(Enum(MatchStars))
    state_id = Column(Integer, ForeignKey("match_state.id"))
    tournament_id = Column(Integer, ForeignKey('tournament.id'))
    url = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"Match(id={self.id!r})"

    def to_domain_object(self, session: Session):
        team1 = get_team(self.team1_id, session)
        team2 = get_team(self.team2_id, session)
        tournament = db.get_tournament(self.tournament_id, session)
        match_state = db.get_match_state(self.state_id, session)

        return domain.match.Match(team1=team1.to_domain_object(), team2=team2.to_domain_object(),
                                  time_utc=datetime.datetime.fromtimestamp(self.unix_time_utc_sec),
                                  stars=self.stars,
                                  tournament=tournament.to_domain_object(),
                                  state=match_state.to_domain_object(),
                                  url=self.url)


def add_match_from_domain_object(match: domain.match.Match, session: Session) -> Optional[Match]:
    team1 = Team.from_domain_object(match.team1, session)
    team1_id = team1.id if team1 else add_team(match.team1.name, match.team1.url, session)

    team2 = Team.from_domain_object(match.team2, session)
    team2_id = team2.id if team2 else add_team(match.team2.name, match.team2.url, session)

    state_name = domain.get_match_state_name(match.state)
    state = db.match_state.get_match_state_by_name(state_name, session)
    state_id = state.id if state else db.match_state.add_match_state(state_name, session)

    tournament_id = db.tournament.get_tournament_id_by_name(match.tournament.name, session)
    if tournament_id is None:
        tournament_id = db.tournament.add_tournament_from_domain_object(match.tournament, session)
        if tournament_id is None:
            tournament_id = db.tournament.get_unknown_tournament_id(session)
            if tournament_id is None:
                logging.error(
                    f'failed to add match from domain object: failed to found tournament (name={match.tournament.name})')
                return None

    match = add_match(team1_id, team2_id,
                      int(datetime.datetime.timestamp(match.time_utc)), MatchStars.from_domain_object(match.stars),
                      tournament_id, state_id, match.url, session)

    return match


def add_match(team1_id: Integer, team2_id: Integer, unix_time_sec: int, match_stars: MatchStars, tournament_id: Integer,
              state_id: Integer, url: str, session: Session) -> Optional[Match]:
    team1 = get_team(team1_id, session)
    if team1 is None:
        logging.error(f'failed to add match because team1 (id={team1_id}) is not found')
        return None

    team2 = get_team(team2_id, session)
    if team2 is None:
        logging.error(f'failed to add match because team2 (id={team2_id}) is not found')
        return None

    match = get_match_by_url(url, session)
    if match is None:
        match = Match(unix_time_utc_sec=unix_time_sec, team1_id=team1_id, team2_id=team2_id, stars=match_stars,
                      state_id=state_id, tournament_id=tournament_id, url=url)
        try:
            session.add(match)
            session.commit()
            logging.info(
                f"Match added: team1 (id={team1.id}, name={team1.name}) vs team2 (id={team2.id}, name={team2.name}) "
                f"with the status (id={state_id}) at {str(datetime.datetime.fromtimestamp(match.unix_time_utc_sec))}")
            return match
        except Exception as e:
            logging.error(f"Failed to add match between team1 (id={team1_id}) and team2 (id={team2_id}) at "
                          f"{datetime.datetime.fromtimestamp(unix_time_sec)}: {e}")
            return None

    return match


# def get_match(match_id: Integer) -> Optional[Match]:
#     with Session(get_engine()) as session:
#         return session.get(Match, match_id)


def get_match_by_url(match_url: str, session: Session) -> Optional[Match]:
    return session.query(Match).filter(Match.url == match_url).first()


def get_match_id_by_url(match_url: str, session: Session) -> Optional[Integer]:
    ret = session.query(Match).filter(Match.url == match_url).first()
    if ret is None:
        return None
    return ret.id


# def get_upcoming_matches_in_datetime_interval(start_from: int, until_to: int, session) -> List[Match]:
#     return session.query(Match)\
#         .filter(and_(start_from < Match.unix_time_utc_sec, Match.unix_time_utc_sec < until_to))\
#         .all()
