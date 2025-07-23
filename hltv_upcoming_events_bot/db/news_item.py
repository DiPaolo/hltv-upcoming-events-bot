import datetime
import logging
from typing import Optional, List

from sqlalchemy import Column, Integer, String, DateTime, Float, desc, and_, ForeignKey
from sqlalchemy.orm import Session

from hltv_upcoming_events_bot import domain, db
from hltv_upcoming_events_bot.db import GameType
from hltv_upcoming_events_bot.db.common import Base
from hltv_upcoming_events_bot.db.news_item_sent import NewsItemSent

_logger = logging.getLogger('hltv_upcoming_events_bot.db')


class NewsItem(Base):
    __tablename__ = "news_item"
    id = Column(Integer, primary_key=True)
    game_type_id = Column(Integer, ForeignKey('game_type.id'))
    date_time_utc = Column(DateTime(timezone=True), nullable=False)
    title = Column(String, nullable=False)
    short_desc = Column(String)
    url = Column(String, nullable=False, unique=True)
    comment_count = Column(Integer)
    comment_avg_hour = Column(Float)

    def __repr__(self):
        return (f"News_item(id={self.id!r}, game_type_id={self.game_type_id}, datetime={self.date_time_utc}, "
                f"title={self.title!r}, url={self.url!r})")

    def to_domain_object(self, session: Session):
        game_type = db.get_game_type(self.game_type_id, session)
        if game_type is None:
            game_type = domain.GameType.UNKNOWN

        return domain.NewsItem(game_type=game_type, date_time_utc=self.date_time_utc, title=self.title,
                               short_desc=self.short_desc, url=self.url, comment_count=self.comment_count,
                               comment_avg_hour=self.comment_avg_hour)


def add_news_item_from_domain_object(news_item: domain.NewsItem, session: Session) -> Optional[NewsItem]:
    game_type = db.get_game_type_by_name(str(news_item.game_type), session)
    if game_type is None:
        return None

    return add_news_item(game_type.id, news_item.date_time_utc, news_item.title, news_item.short_desc, news_item.url,
                         news_item.comment_count, news_item.comment_avg_hour, session)


def add_news_item(game_type_id: Integer, date_time_utc: datetime.date, title: str, short_description: str, url: str,
                  comment_count: int, comment_avg_hour: float, session: Session) -> Optional[NewsItem]:
    news_item = get_news_item_by_url(url, session)
    if news_item is None:
        news_item = NewsItem(game_type_id=game_type_id, date_time_utc=date_time_utc, title=title,
                             short_desc=short_description, url=url, comment_count=comment_count,
                             comment_avg_hour=comment_avg_hour)
        try:
            session.add(news_item)
            # session.commit()
            # _logger.info(f"news item added: {date_time_utc}, '{news_item.title}' ({news_item.url})")
            return news_item
        except Exception as e:
            _logger.error(f"failed to add news item (datetime={date_time_utc}, title={title}, url={url}): {e}")
            return None

    return news_item


def get_news_item(news_item_id: Integer, session: Session) -> Optional[NewsItem]:
    return session.get(NewsItem, news_item_id)


def get_news_item_by_url(url: str, session: Session) -> Optional[NewsItem]:
    return session.query(NewsItem).filter(NewsItem.url == url).first()


def get_recent_news_items(since_time_utc: datetime.datetime, max_count: int, session: Session) -> List[NewsItem]:
    return session.query(NewsItem) \
        .filter(NewsItem.date_time_utc >= since_time_utc) \
        .order_by(desc(NewsItem.comment_avg_hour)) \
        .limit(max_count)


def get_recent_news_items_for_chat(game_type_id: Integer, chat_id: Integer, since_time_utc: datetime.datetime,
                                   max_count: int, session: Session) -> List[NewsItem]:
    rows = session.query(NewsItem) \
        .join(GameType) \
        .outerjoin(NewsItemSent) \
        .order_by(desc(NewsItem.comment_avg_hour)) \
        .filter(and_(NewsItem.date_time_utc >= since_time_utc, GameType.id == game_type_id)) \
        .add_entity(NewsItemSent) \
        .all()

    out = list()

    cur_news_item = None
    cur_news_item_sent_for_chat = False
    for row in rows:
        if cur_news_item is None:
            cur_news_item = row.NewsItem
        elif row.NewsItem.id != cur_news_item.id:
            if not cur_news_item_sent_for_chat and cur_news_item is not None:
                out.append(cur_news_item)
                if len(out) == max_count:
                    return out

            cur_news_item = row.NewsItem
            cur_news_item_sent_for_chat = False

        if row.NewsItemSent is not None and row.NewsItemSent.chat_id == chat_id:
            cur_news_item_sent_for_chat = True

    if not cur_news_item_sent_for_chat and cur_news_item is not None:
        out.append(cur_news_item)
        if len(out) == max_count:
            return out

    return out


def update_news_item(news_item_id: Integer, date_time_utc: datetime.date, title: str, short_description: str,
                     comment_count: int, comment_avg_hour: float, session: Session):
    news_item = get_news_item(news_item_id, session)
    if news_item is None:
        return

    changed_props = list()

    changes = [
        [date_time_utc, 'date_time_utc'],
        [title, 'title'],
        [short_description, 'short_desc'],
        [comment_count, 'comment_count'],
        [comment_avg_hour, 'comment_avg_hour'],
    ]

    for change in changes:
        if change[0] is not None:
            old_value = getattr(news_item, change[1])
            if change[0] != old_value:
                setattr(news_item, change[1], change[0])
                changed_props.append((old_value, change[0]))

    updated_props_str = ', '.join([f'{p[0]} -> {p[1]}' for p in changed_props]) if len(
        changed_props) > 0 else 'no changes'

    # session.commit()

    _logger.info(f'news item updated: {updated_props_str}')
