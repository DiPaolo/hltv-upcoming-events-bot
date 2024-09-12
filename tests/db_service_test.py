import datetime

import pytest

import hltv_upcoming_events_bot.service.db as db_service


@pytest.mark.parametrize('chat_tg_id', [
    123, 234
])
@pytest.mark.parametrize('time_delta,expected_count', [
    (datetime.timedelta(seconds=5), 0),
    (datetime.timedelta(minutes=10), 1),
    (datetime.timedelta(minutes=15), 2),
    (datetime.timedelta(hours=2), 3),
    (datetime.timedelta(days=1), 4),
])
@pytest.mark.usefixtures('db_engine', 'db_data_news_items')
def test_get_recent_news_items_for_chat(chat_tg_id, time_delta, expected_count, db_engine, db_data_news_items):
    now = datetime.datetime.now()

    news_items = db_service.get_recent_news_for_chat(chat_tg_id, now - time_delta, 20, db_engine)

    assert len(news_items) == expected_count

    expected_news_list = list(filter(lambda ni: now - time_delta <= ni.date_time_utc <= now, db_data_news_items))
    assert set(news_items) == set(expected_news_list)


@pytest.mark.usefixtures('db_engine', 'db_data_news_items')
def test_get_recent_news_items_for_chat_with_mark_as_sent(db_engine, db_data_news_items):
    now = datetime.datetime.now()

    #
    # first user
    #

    news_items = db_service.get_recent_news_for_chat(123, now - datetime.timedelta(hours=2), 20, db_engine)

    assert len(news_items) == 3
    expected_news_list = list(
        filter(lambda ni: now - datetime.timedelta(hours=2) <= ni.date_time_utc <= now, db_data_news_items))
    assert set(news_items) == set(expected_news_list)

    db_service.mark_news_items_as_sent(news_items, [123], db_engine)

    news_items = db_service.get_recent_news_for_chat(123, now - datetime.timedelta(days=1), 20, db_engine)

    assert len(news_items) == 1
    expected_news_list = list(set(expected_news_list).symmetric_difference(set(db_data_news_items)))
    assert set(news_items) == set(expected_news_list)

    db_service.mark_news_items_as_sent(news_items, [123], db_engine)

    news_items = db_service.get_recent_news_for_chat(123, now - datetime.timedelta(days=100), 20, db_engine)

    assert len(news_items) == 0

    #
    # second user
    #

    news_items = db_service.get_recent_news_for_chat(234, now - datetime.timedelta(hours=2), 20, db_engine)

    assert len(news_items) == 3
    expected_news_list = list(
        filter(lambda ni: now - datetime.timedelta(hours=2) <= ni.date_time_utc <= now, db_data_news_items))
    assert set(news_items) == set(expected_news_list)

    db_service.mark_news_items_as_sent(news_items, [234], db_engine)

    news_items = db_service.get_recent_news_for_chat(234, now - datetime.timedelta(days=1), 20, db_engine)

    assert len(news_items) == 1
    expected_news_list = list(set(expected_news_list).symmetric_difference(set(db_data_news_items)))
    assert set(news_items) == set(expected_news_list)

    db_service.mark_news_items_as_sent(news_items, [234], db_engine)

    news_items = db_service.get_recent_news_for_chat(234, now - datetime.timedelta(days=100), 20, db_engine)

    assert len(news_items) == 0
