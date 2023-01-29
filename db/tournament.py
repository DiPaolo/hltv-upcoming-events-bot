import logging
from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

import domain.tournament
from db.common import Base, get_engine

_UNKNOWN_TOURNAMENT_NAME = 'Unknown'


class Tournament(Base):
    __tablename__ = "tournament"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    url = Column(String, unique=True)
    hltv_id = Column(Integer, unique=True)

    def __repr__(self):
        return f"Tournament(id={self.id!r}, name={self.name!r}, url={self.url!r})"

    # def to_domain_object(self):
    #     return domain.match.Match()


def add_tournament_from_domain_object(tournament: domain.tournament.Tournament, session: Session = None) -> Optional[
    Integer]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    return add_tournament(tournament.name, tournament.url, tournament.hltv_id)


def add_tournament(name: str, url: str, hltv_id: int, session: Session = None) -> Optional[Integer]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    tournament = Tournament(name, url, hltv_id)
    cur_session.add(tournament)

    # created at the beginning of the function
    if not session:
        try:
            cur_session.commit()
            logging.info(
                f"Tournament added: name={tournament.name}, url={tournament.url}")
        except Exception as e:
            print(f"ERROR failed to add tournament (name={tournament.name}, url={tournament.url}): {e}")

    return tournament.id


def get_tournament(tournament_id: Integer, session: Session = None) -> Optional[Tournament]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    ret = cur_session.get(Tournament, tournament_id)

    # created at the beginning of the function
    if not session:
        cur_session.commit()

    return ret


def get_tournament_by_name(name: str, session: Session = None) -> Optional[Tournament]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    try:
        tournament = cur_session.query(Tournament).filter(Tournament.name == name).first()
    except BaseException as e:
        logging.error(f"failed to get tournament (name={name}) from DB: {e}")
        return None

    return tournament


def add_unknown_tournament(session: Session = None) -> Optional[Integer]:
    return add_tournament(_UNKNOWN_TOURNAMENT_NAME, '', -1, session)


def get_unknown_tournament(session: Session = None) -> Optional[Tournament]:
    return get_tournament_by_name(_UNKNOWN_TOURNAMENT_NAME, session)
