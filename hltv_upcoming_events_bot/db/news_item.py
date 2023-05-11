import datetime
import logging
from typing import Optional, Dict, List

from sqlalchemy import Column, Integer, String, DateTime, Float, desc
from sqlalchemy.orm import Session

from hltv_upcoming_events_bot import domain
from hltv_upcoming_events_bot.db.common import Base


class NewsItem(Base):
    __tablename__ = "news_item"
    id = Column(Integer, primary_key=True)
    date_time_utc = Column(DateTime(timezone=True), nullable=False)
    title = Column(String, nullable=False)
    short_desc = Column(String)
    url = Column(String, nullable=False, unique=True)
    comment_count = Column(Integer)
    comment_avg_hour = Column(Float)

    def __repr__(self):
        return f"News_item(id={self.id!r}, datetime={self.date_time_utc}, title={self.title!r}, url={self.url!r})"

    def to_domain_object(self):
        return domain.NewsItem(date_time_utc=self.date_time_utc, title=self.title,
                               short_desc=self.short_desc, url=self.url, comment_count=self.comment_count,
                               comment_avg_hour=self.comment_avg_hour)


def add_news_item_from_domain_object(news_item: domain.NewsItem, session: Session) -> Optional[NewsItem]:
    return add_news_item(news_item.date_time_utc, news_item.title, news_item.short_desc, news_item.url,
                         news_item.comment_count, news_item.comment_avg_hour, session)


def add_news_item(date_time_utc: datetime.date, title: str, short_description: str, url: str, comment_count: int,
                  comment_avg_hour: float, session: Session) -> Optional[NewsItem]:
    news_item = get_news_item_by_url(url, session)
    if news_item is None:
        news_item = NewsItem(date_time_utc=date_time_utc, title=title, short_desc=short_description, url=url,
                             comment_count=comment_count, comment_avg_hour=comment_avg_hour)
        try:
            session.add(news_item)
            session.commit()
            logging.info(f"news item added: {date_time_utc}, '{news_item.title}' ({news_item.url})")
            return news_item
        except Exception as e:
            logging.error(f"failed to add news item (datetime={date_time_utc}, title={title}, url={url}): {e}")
            return None

    return news_item


def get_news_item(news_item_id: Integer, session: Session) -> Optional[NewsItem]:
    return session.get(NewsItem, news_item_id)


def get_news_item_by_url(url: str, session: Session) -> Optional[NewsItem]:
    return session.query(NewsItem).filter(NewsItem.url == url).first()


def get_recent_news_items(since_time_utc: datetime.datetime, max_count: int, session: Session) -> List[NewsItem]:
    return session.query(NewsItem)\
        .filter(NewsItem.date_time_utc >= since_time_utc)\
        .order_by(desc(NewsItem.comment_avg_hour))\
        .limit(max_count)


def update_news_item(news_item_id: Integer, date_time_utc: datetime.date, title: str, short_description: str,
                     comment_count: int, comment_avg_hour: float, session: Session):
    news_item = get_news_item(news_item_id, session)
    if news_item is None:
        return

    news_item.date_time_utc = date_time_utc
    news_item.title = title
    news_item.short_desc = short_description
    news_item.comment_count = comment_count
    news_item.comment_avg_hour = comment_avg_hour

    session.commit()
