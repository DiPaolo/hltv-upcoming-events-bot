import datetime
import os.path
import pathlib
from typing import Callable, List

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from hltv_upcoming_events_bot.db import chat, news_item
from hltv_upcoming_events_bot.db.chat import Chat
from hltv_upcoming_events_bot.domain import NewsItem


@pytest.fixture(scope="module")
def read_input_file() -> Callable[[str], str]:
    def _read_input_json(base_filename: str) -> str:
        cur_file_path = pathlib.Path(__file__).parent.resolve()
        data_dir = os.path.join(cur_file_path, 'data')
        with open(os.path.join(data_dir, base_filename), 'r') as f:
            return f.read()

    return _read_input_json


# _CHAT_IDS = [111, 222, 333]
_TG_IDS = [123, 234, 345]
_CHAT_TITLES = ['chat_title 1', 'chat_title 2', 'chat_title 3']
_CHAT_TYPES = ['private chat type', 'public chat type', 'unknown chat type']

_NEWS_ITEMS = [
    NewsItem(datetime.datetime.now() - datetime.timedelta(minutes=1),
             'News Item Title 111', 'News Item Short Desc 111', 'http://news1.com/111.html', 11, 11.11),
    NewsItem(datetime.datetime.now() - datetime.timedelta(minutes=12),
             'News Item Title 222', 'News Item Short Desc 222', 'http://news2.com/222.html', 22, 22.22),
    NewsItem(datetime.datetime.now() - datetime.timedelta(hours=1),
             'News Item Title 333', 'News Item Short Desc 333', 'http://news3.com/333.html', 33, 33.33),
    NewsItem(datetime.datetime.now() - datetime.timedelta(hours=12, minutes=34),
             'News Item Title 444', 'News Item Short Desc 444', 'http://news4.com/444.html', 44, 44.44),
]


@pytest.fixture(scope='module')
def db_engine():  # 1
    # connection = sqlite3.connect(':memory:')
    # db_session = connection.cursor()
    # yield db_session
    # connection.close()

    engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
    session = Session(engine)
    Chat().metadata.create_all(engine)

    for i in range(3):
        chat.add_chat_from_domain_object(Chat(telegram_id=_TG_IDS[i], title=_CHAT_TITLES[i], type=_CHAT_TYPES[i]),
                                         session)

    for ni in _NEWS_ITEMS:
        news_item.add_news_item_from_domain_object(ni, session)

    session.commit()

    yield engine


@pytest.fixture(scope='function')
def db_data_news_items() -> List[NewsItem]:
    return _NEWS_ITEMS
