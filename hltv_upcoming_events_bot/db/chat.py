import logging
from typing import Optional, List

from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from hltv_upcoming_events_bot import domain
from hltv_upcoming_events_bot.db.common import Base


class Chat(Base):
    __tablename__ = "chat"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    title = Column(String)
    type = Column(String)

    def __repr__(self):
        return f"Chat(id={self.id!r})"

    def to_domain_object(self):
        return domain.Chat(telegram_id=self.telegram_id, title=self.title, type=self.type)


def add_chat_from_domain_object(chat: domain.Chat, session: Session) -> Optional[Integer]:
    return add_chat(chat.telegram_id, chat.title, chat.type, session)


def add_chat(telegram_id: int, title: str, type: str, session: Session) -> Optional[Integer]:
    chat = Chat(telegram_id=telegram_id, title=title, type=type)

    try:
        session.add(chat)
        session.commit()
        _logger.info(
            f"chat added (id={chat.id}, telegram_id={chat.telegram_id}, title={chat.title}, type={chat.type})")
    except Exception as e:
        _logger.error(f"failed to add chat (title={title}, telegram_id={telegram_id}): {e}")

    return chat.id


def get_chat(chat_id: Integer, session: Session) -> Optional[Chat]:
    return session.get(Chat, chat_id)


def get_chat_by_telegram_id(telegram_id: int, session: Session) -> Optional[Chat]:
    try:
        return session.query(Chat).filter(Chat.telegram_id == telegram_id).one()
    except NoResultFound:
        return None


def get_chats(session: Session) -> List[Chat]:
    return session.query(Chat).all()
