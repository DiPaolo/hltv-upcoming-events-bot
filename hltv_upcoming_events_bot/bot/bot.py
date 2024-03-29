import datetime

import telegram
from telegram import ParseMode, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

import hltv_upcoming_events_bot
import hltv_upcoming_events_bot.service.db as db_service
import hltv_upcoming_events_bot.service.matches as matches_service
import hltv_upcoming_events_bot.service.news as news_service
import hltv_upcoming_events_bot.service.tg_notifier as tg_notifier_service
from hltv_upcoming_events_bot import config
from hltv_upcoming_events_bot.bot.utils import log_command


def start_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine)
    engine.message.reply_text(_get_help_text())


def get_upcoming_matches_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine)

    upcoming_matches_str = matches_service.get_upcoming_matches_str()
    send_message(engine.effective_chat.id, upcoming_matches_str)


def get_recent_news_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine)

    tg_id = engine.effective_chat.id

    recent_news = news_service.get_recent_news_for_chat(
        tg_id, datetime.datetime.utcnow() - datetime.timedelta(hours=24), 3)
    recent_news_str = news_service.get_recent_news_str(recent_news)
    db_service.mark_news_items_as_sent(recent_news, [tg_id])

    send_message(engine.effective_chat.id, recent_news_str)


def subscribe_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine)
    ret = tg_notifier_service.add_subscriber(engine.effective_chat.id)
    if ret == tg_notifier_service.RetCode.OK:
        send_message(engine.effective_chat.id, 'Подписали вас. Завтра придет уведомление о матчах')
    elif ret == tg_notifier_service.RetCode.ALREADY_EXIST:
        send_message(engine.effective_chat.id, 'Вы уже подписаны 👌')
    else:
        send_message(engine.effective_chat.id, 'К сожалению, произошла ошибка. Не удалось подписаться :(')


def unsubscribe_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine)
    ret = tg_notifier_service.remove_subscriber(engine.effective_chat.id)
    if ret == tg_notifier_service.RetCode.OK:
        send_message(engine.effective_chat.id, 'Отписали вас от ежедневных обновлений. Нам очень жаль :(')
    elif ret == tg_notifier_service.RetCode.NOT_EXIST:
        send_message(engine.effective_chat.id, 'Похоже, что вы и не были подписаны 🤔')
    else:
        send_message(engine.effective_chat.id, 'К сожалению, проихошла ошибка. Не удалось отписать вас')


def help_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine)
    engine.message.reply_text(_get_help_text(), parse_mode=ParseMode.HTML)


def version_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine)
    engine.message.reply_text(hltv_upcoming_events_bot.__version__, parse_mode=ParseMode.HTML)


def send_message(chat_id: int, msg: str):
    bot = telegram.Bot(config.BOT_TOKEN)
    ret = bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    pass


def start(token: str) -> None:
    engine = Updater(token)
    dispatcher = engine.dispatcher

    commands_str = '''
    matches - список интересных матчей на сегодня
    news - последние интересные новости
    subscribe - подписаться на уведомления о матчах и новостях
    unsubscribe - отписаться от уведомлений
    help - вывести справочную информацию
    version - показать текущую версию бота
    '''

    # commands
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("matches", get_upcoming_matches_command))
    dispatcher.add_handler(CommandHandler('news', get_recent_news_command))
    dispatcher.add_handler(CommandHandler("subscribe", subscribe_command))
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("version", version_command))

    engine.start_polling()
    engine.idle()


def _get_help_text() -> str:
    return "Бот, который:\n" \
           "  - уведомляет о сегодняшних интересных матчах в CS:GO\n" \
           "  - сразу дает ссылки на русскоязычную трансляцию\n" \
           "  - может выдать список ближайших матчей по требованию (/matches)\n" \
           "\n" \
           "Чтобы подписаться на уведомления раз в день, используй команду /subscribe\n" \
           "\n" \
           "Выдает только игры со звездами HLTV, то есть наиболее интересные\n" \
           "\n" \
           "Контакт: @DiPaolo"
