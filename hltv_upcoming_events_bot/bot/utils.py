import datetime
import logging

from telegram import Update

import hltv_upcoming_events_bot.db as db


def log_command(engine: Update):
    cur_time = datetime.datetime.utcnow()
    u = engine.effective_user

    session = db.create_session()

    user = db.get_user_by_telegram_id(u.id, session)
    if user is None:
        user_id = db.add_user(u.id, u.username, u.first_name, u.last_name, u.is_bot, u.is_premium, u.language_code,
                              session)
        user = db.get_user(user_id, session)
        if user is None:
            logging.error(
                f"Failed to log command: failed to create user (telegram_id={u.id}, username={u.username}, is_bot={u.is_bot})")
            return

    m = engine.effective_message

    texts = list()

    query = engine.callback_query
    if query is not None:
        texts.append(f"button data: '{query.data}'")

    location = engine.effective_message.location
    if location is not None:
        texts.append(f"location: {location.latitude}, {location.longitude}")

    texts.append(f"text: '{m.text}'")

    db.add_user_request(user.id, cur_time, m.date, m.message_id, ', '.join(texts), session)


def log_send_message(engine: Update):
    cur_time = datetime.datetime.utcnow()
    u = engine.effective_user

    session = db.create_session()

    user = db.get_user_by_telegram_id(u.id, session)
    if user is None:
        user_id = db.add_user(u.id, u.username, u.first_name, u.last_name, u.is_bot, u.is_premium, u.language_code,
                              session)
        user = db.get_user(user_id, session)
        if user is None:
            logging.error(
                f"Failed to log command: failed to create user (telegram_id={u.id}, username={u.username}, is_bot={u.is_bot})")
            return

    m = engine.effective_message

    texts = list()

    query = engine.callback_query
    if query is not None:
        texts.append(f"button data: '{query.data}'")

    location = engine.effective_message.location
    if location is not None:
        texts.append(f"location: {location.latitude}, {location.longitude}")

    texts.append(f"text: '{m.text}'")

    db.add_user_request(user.id, cur_time, m.date, m.message_id, ', '.join(texts), session)
