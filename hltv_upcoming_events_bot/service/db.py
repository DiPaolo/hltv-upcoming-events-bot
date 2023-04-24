from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from hltv_upcoming_events_bot import db
from hltv_upcoming_events_bot import domain
from hltv_upcoming_events_bot.db.common import get_engine


def add_match(match: domain.Match):
    with Session(get_engine()) as session:
        db.add_match_from_domain_object(match, session)


def add_streamer(streamer: domain.Streamer):
    with Session(get_engine()) as session:
        db.add_streamer_from_domain_object(streamer, session)


def get_upcoming_matches_in_datetime_interval(start_from: int, until_to: int) -> List[domain.Match]:
    out = list()
    with Session(get_engine()) as session:
        matches = session.query(db.Match).filter(
            and_(start_from < db.Match.unix_time_utc_sec, db.Match.unix_time_utc_sec < until_to)).all()

        for match in matches:
            out.append(match.to_domain_object(session))

    return out
