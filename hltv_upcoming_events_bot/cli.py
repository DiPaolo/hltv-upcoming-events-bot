#!/usr/bin/env python
import logging
import os
import threading
import time

import schedule
import telegram
from telegram import Update, ForceReply, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

from hltv_upcoming_events_bot import config
import hltv_upcoming_events_bot
import hltv_upcoming_events_bot.service.matches
import hltv_upcoming_events_bot.service.tg_notifier

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


def start(engine: Update, context: CallbackContext) -> None:
    user = engine.effective_user
    engine.message.reply_markdown_v2(
        fr'Привет, {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def get_upcoming_matches_command(engine: Update, context: CallbackContext) -> None:
    upcoming_matches_str = hltv_upcoming_events_bot.service.matches.get_upcoming_matches_str()
    engine.message.reply_text('ничего интересного сегодня :(' if not upcoming_matches_str else upcoming_matches_str,
                              parse_mode=ParseMode.HTML)


def subscribe_command(engine: Update, context: CallbackContext) -> None:
    hltv_upcoming_events_bot.service.tg_notifier.add_subscriber(engine.effective_chat.id)


def help_command(engine: Update, context: CallbackContext) -> None:
    engine.message.reply_text("Бот, который:\n"
                              "  - уведомляет о сегодняшних интересных матчах в CS:GO\n"
                              "  - сразу дает ссылки на русскоязычную трансляцию\n"
                              "  - может выдать список ближайших матчей по требованию (/matches)\n"
                              "\n"
                              "Чтобы подписаться на уведомления раз в день, используй команду /subscribe\n"
                              "\n"
                              "Выдает только игры со звездами HLTV, то есть наиболее интересные",
                              parse_mode=ParseMode.HTML)


def version_command(engine: Update, context: CallbackContext) -> None:
    engine.message.reply_text(hltv_upcoming_events_bot.__version__, parse_mode=ParseMode.HTML)


def send_message(chat_id: int, msg: str):
    bot = telegram.Bot(token=os.getenv('DP_TG_BOT_TOKEN'))
    bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.HTML)


def main() -> None:
    engine = Updater(os.getenv('DP_TG_BOT_TOKEN'))

    dispatcher = engine.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("matches", get_upcoming_matches_command))
    dispatcher.add_handler(CommandHandler("subscribe", subscribe_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("version", version_command))

    engine.start_polling()

    engine.idle()


def _get_env_val_as_bool(val) -> bool:
    return val if type(val) == bool else val.lower() in ['true', 'yes', '1']


class ScheduleThread(threading.Thread):
    @classmethod
    def run(cls):
        while True:
            schedule.run_pending()
            time.sleep(1)


def app_init():
    continuous_thread = ScheduleThread()
    continuous_thread.start()


def cli():
    env_debug_val = os.environ.get('DP_TG_BOT_DEBUG')
    if env_debug_val:
        config.DEBUG = _get_env_val_as_bool(env_debug_val)

    logging.info('Starting bot...')

    app_init()
    hltv_upcoming_events_bot.service.matches.init()
    hltv_upcoming_events_bot.service.tg_notifier.init(send_message)

    main()
