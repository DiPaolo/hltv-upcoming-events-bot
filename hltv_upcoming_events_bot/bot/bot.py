import telegram
from telegram import ParseMode, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

import hltv_upcoming_events_bot
import hltv_upcoming_events_bot.service.matches as matches_service
import hltv_upcoming_events_bot.service.tg_notifier as tg_notifier_service
import hltv_upcoming_events_bot.service.timezone as timezone_service
from hltv_upcoming_events_bot import config
from hltv_upcoming_events_bot.bot.utils import log_command


def start_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine)
    send_message(engine.effective_chat.id, _get_help_text())


def get_upcoming_matches_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine)
    upcoming_matches_str = matches_service.get_upcoming_matches_str()
    send_message(engine.effective_chat.id,
                 'ничего интересного сегодня :(' if not upcoming_matches_str else upcoming_matches_str)


def subscribe_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine)
    tg_notifier_service.add_subscriber(engine.effective_chat.id)


def unsubscribe_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine)
    tg_notifier_service.remove_subscriber(engine.effective_chat.id)


def set_timezone_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine)

    timezone_text = ' '.join(context.args)

    timezone_offset = timezone_service.parse_timezone_offset_str(timezone_text)
    if timezone_offset is None:
        send_message(engine.effective_chat.id, 'Неверно указана временная зона.\n'
                                               '\n'
                                               'Укажите временную зону в виде числа, например:\n'
                                               '4 - московское время (UTC+4)\n'
                                               '7 - новосибирское время (UTC+7)\n'
                                               '-3 - аргентинское время (UTC-3)')
        return

    timezone = timezone_service.set_user_timezone(engine.effective_chat.id, timezone_offset)
    if timezone is None:
        send_message(engine.effective_chat.id,
                     'Ошибка установки временной зоны. Проверьте правильнсть введенных данных и повторите попытку.')
        return

    send_message(engine.effective_chat.id, f"Временная зона теперь {timezone.tzname(None)}")


def get_timezone_command(engine: Update, context: CallbackContext) -> None:
    send_message(timezone_service.get_user_timezone(engine.effective_chat.id))


def help_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine)
    send_message(engine.effective_chat.id, _get_help_text())


def version_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine)
    send_message(engine.effective_chat.id, hltv_upcoming_events_bot.__version__)


def send_message(chat_id: int, msg: str):
    bot = telegram.Bot(config.BOT_TOKEN)
    bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def start(token: str) -> None:
    engine = Updater(token)
    dispatcher = engine.dispatcher

    # commands
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("matches", get_upcoming_matches_command))
    dispatcher.add_handler(CommandHandler("subscribe", subscribe_command))
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    dispatcher.add_handler(CommandHandler("settimezone", set_timezone_command))
    dispatcher.add_handler(CommandHandler("timezone", get_timezone_command))
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
