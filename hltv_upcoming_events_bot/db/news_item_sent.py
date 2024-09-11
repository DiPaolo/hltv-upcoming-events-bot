import logging
from typing import Optional, List

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Session

from hltv_upcoming_events_bot.db.common import Base


class NewsItemSent(Base):
    __tablename__ = "news_item_sent"
    __table_args__ = (
        UniqueConstraint('news_item_id', 'chat_id', name='unique_news_item_id_and_chat_id'),
    )
    id = Column(Integer, primary_key=True)
    news_item_id = Column(Integer, ForeignKey('news_item.id'))
    chat_id = Column(Integer, ForeignKey('chat.id'))

    def __repr__(self):
        return f"NewsItemSent(id={self.id!r}, news_item_id={self.news_item_id}, chat_id={self.chat_id!r})"

    # def to_domain_object(self):
    #     return domain.NewsItem(date_time_utc=self.date_time_utc, title=self.title,
    #                            short_desc=self.short_desc, url=self.url, comment_count=self.comment_count,
    #                            comment_avg_hour=self.comment_avg_hour)


def add_news_item_sent(news_item_id: Integer, chat_id: Integer, session: Session) -> Optional[Integer]:
    news_item_sent = NewsItemSent(news_item_id=news_item_id, chat_id=chat_id)

    try:
        session.add(news_item_sent)
        session.commit()
        logging.info(f"news item sent added: news_item (id={news_item_id}), chat (id={chat_id})")
    except Exception as e:
        logging.error(f"failed to add news item sent (news_item_id={news_item_id}, chat_id={chat_id}): {e}")
        return None

    return news_item_sent.id


def get_news_item_sent_all(Integer, session: Session) -> List[NewsItemSent]:
    return session \
        .query(NewsItemSent) \
        .all()


def get_news_item_sent_by_news_item_id(news_item_id: Integer, session: Session) -> List[NewsItemSent]:
    return session \
        .query(NewsItemSent) \
        .filter(NewsItemSent.news_item_id == news_item_id) \
        .all()
