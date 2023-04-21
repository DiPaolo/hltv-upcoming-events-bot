import logging
from typing import Optional, Dict, List

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from hltv_upcoming_events_bot.db.common import Base, get_engine


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_bot = Column(Boolean)
    is_premium = Column(Boolean)
    language_code = Column(String)

    def __repr__(self):
        return f"User(id={self.id!r})"

    # def to_domain_object(self):
    #     return domain.match.Match()


# def add_match_from_domain_object(match: tabletka_tomsk_bot.domain.match.Match, session: Session = None) -> Optional[
#     Match]:
#     cur_session = session if session else Session(get_engine())
#     if cur_session is None:
#         return None
#
#     team1 = Team.from_domain_object(match.team1)
#     team1_id = team1.id if team1 else add_team(match.team1.name, match.team1.url)
#
#     team2 = Team.from_domain_object(match.team2)
#     team2_id = team2.id if team2 else add_team(match.team2.name, match.team2.url)
#
#     state_name = get_match_state_name(match.state)
#     state = tabletka_tomsk_bot.db.match_state.get_match_state_by_name(state_name)
#     state_id = state.id if state else tabletka_tomsk_bot.db.match_state.add_match_state(state_name)
#
#     tournament = tabletka_tomsk_bot.db.tournament.get_tournament_by_name(match.tournament.name)
#     if tournament is None:
#         tournament = tabletka_tomsk_bot.db.tournament.add_tournament_from_domain_object(match.tournament)
#         if tournament is None:
#             tournament = tabletka_tomsk_bot.db.tournament.get_unknown_tournament()
#             if tournament is None:
#                 logging.error(
#                     f'failed to add match from domain object: failed to found tournament (name={match.tournament.name})')
#                 return None
#
#     return add_match(team1_id, team2_id,
#                      int(datetime.datetime.timestamp(match.time_utc)), MatchStars.from_domain_object(match.stars),
#                      tournament.id, state_id, match.url)


def add_user(telegram_id: int, username: str, first_name: str, last_name: str, is_bot: bool, is_premium: bool,
             language_code: str, session: Session = None) -> Optional[Integer]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    match = User(telegram_id=telegram_id, username=username, first_name=first_name, last_name=last_name, is_bot=is_bot,
                 is_premium=is_premium, language_code=language_code)

    try:
        cur_session.add(match)
        cur_session.commit()
        logging.info(
            f"User added (id={match.id}, username={match.username}, telegram_id={match.telegram_id})")
    except Exception as e:
        print(f"ERROR failed to add uesr (username={username}, telegram_id={telegram_id}): {e}")

    return match.id


def get_user(user_id: Integer, session: Session = None) -> Optional[User]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None
    return cur_session.get(User, user_id)


def get_user_by_telegram_id(telegram_id: Integer, session: Session = None) -> Optional[User]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    try:
        ret = cur_session.query(User).filter(User.telegram_id == telegram_id).one()
    except NoResultFound:
        ret = None

    # # created at the beginning of the function
    # if not session:
    #     cur_session.commit()

    return ret


def get_users(session: Session = None) -> List[User]:
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return list()

    ret = cur_session.query(User).all()

    return ret


def update_user(user_id: Integer, props: Dict, session: Session = None):
    cur_session = session if session else Session(get_engine())
    if cur_session is None:
        return None

    skin = get_user(user_id, cur_session)
    for key, value in props.items():
        setattr(skin, key, value)

    # # created at the beginning of the function
    # if not session:
    #     cur_session.commit()
