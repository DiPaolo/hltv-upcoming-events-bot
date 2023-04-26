import logging
from typing import Optional, List

from sqlalchemy import Column, Integer, ForeignKey, and_
from sqlalchemy.orm import Session

from hltv_upcoming_events_bot.db.common import Base


class Translation(Base):
    __tablename__ = "translation"
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('match.id'))
    streamer_id = Column(Integer, ForeignKey('streamer.id'))

    def __repr__(self):
        return f"Translation(id={self.id!r}, match_id={self.match_id!r}, streamer_id={self.streamer_id!r})"

    # @staticmethod
    # def from_domain_object(translation_domain: domain.translation.Translation):
    #     return get_translation_by_url(translation_domain.url)

    # def to_domain_object(self):
    #     return domain.translation.Translation(streamer_name=self.streamer_name, language=self.language.name, url=self.url)


# def add_translation_from_domain_object(trans: domain.Translation) -> Optional[Translation]:
#     return add_translation(trans.streamer_name, trans.language.name, trans.url)


def add_translation(match_id: Integer, streamer_id: Integer, session: Session) -> Optional[Integer]:
    translation_id = get_translation(match_id, streamer_id, session)
    if translation_id is not None:
        return translation_id

    translation = Translation(match_id=match_id, streamer_id=streamer_id)
    session.add(translation)

    try:
        session.commit()
        logging.info(f"Translation added (id={translation.id}, match_id={translation.match_id},"
                     f" streamer_id={translation.streamer_id})")
        return translation.id
    except Exception as e:
        logging.error(f"Failed to add translation for match (id='{match_id}') and streamer (id='{streamer_id}'): {e}")
        return None


def get_translations_by_match_id(match_id: Integer, session: Session) -> List[Translation]:
    return session\
        .query(Translation)\
        .filter(Translation.match_id == match_id)\
        .all()


def get_translation(match_id: Integer, streamer_id: Integer, session: Session) -> Optional[Integer]:
    translation = session\
        .query(Translation)\
        .filter(and_(Translation.match_id == match_id, Translation.streamer_id == streamer_id))\
        .first()

    if translation is None:
        return None

    return translation.id

