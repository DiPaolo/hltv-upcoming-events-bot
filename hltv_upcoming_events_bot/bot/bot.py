import datetime
import logging

import telegram
from telegram import ParseMode, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

import hltv_upcoming_events_bot
import hltv_upcoming_events_bot.service.db as db_service
import hltv_upcoming_events_bot.service.matches as matches_service
import hltv_upcoming_events_bot.service.news as news_service
import hltv_upcoming_events_bot.service.tg_notifier as tg_notifier_service
import hltv_upcoming_events_bot.service.timezone as timezone_service
from hltv_upcoming_events_bot import config
from hltv_upcoming_events_bot.bot.utils import log_command

_logger = logging.getLogger('hltv_upcoming_events_bot.bot')


def start_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine, _logger)
    send_message(engine.effective_chat.id, _get_help_text())


def get_upcoming_matches_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine, _logger)

    upcoming_matches_str = matches_service.get_upcoming_matches_str()
    send_message(engine.effective_chat.id, upcoming_matches_str)


def get_recent_news_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine, _logger)

    tg_id = engine.effective_chat.id

    recent_news = news_service.get_recent_news_for_chat(
        tg_id, datetime.datetime.utcnow() - datetime.timedelta(hours=24), 3)
    recent_news_str = news_service.get_recent_news_str(recent_news)
    db_service.mark_news_items_as_sent(recent_news, [tg_id])

    send_message(engine.effective_chat.id, recent_news_str)


def subscribe_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine, _logger)
    ret = tg_notifier_service.add_subscriber(engine.effective_chat.id)
    if ret == tg_notifier_service.RetCode.OK:
        send_message(engine.effective_chat.id, 'Подписали вас. Завтра придет уведомление о матчах')
    elif ret == tg_notifier_service.RetCode.ALREADY_EXIST:
        send_message(engine.effective_chat.id, 'Вы уже подписаны 👌')
    else:
        send_message(engine.effective_chat.id, 'К сожалению, произошла ошибка. Не удалось подписаться :(')


def unsubscribe_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine, _logger)
    ret = tg_notifier_service.remove_subscriber(engine.effective_chat.id)
    if ret == tg_notifier_service.RetCode.OK:
        send_message(engine.effective_chat.id, 'Отписали вас от ежедневных обновлений. Нам очень жаль :(')
    elif ret == tg_notifier_service.RetCode.NOT_EXIST:
        send_message(engine.effective_chat.id, 'Похоже, что вы и не были подписаны 🤔')
    else:
        send_message(engine.effective_chat.id, 'К сожалению, проихошла ошибка. Не удалось отписать вас')


def set_timezone_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine, _logger)
    _set_timezone_internal_command(engine, context)


def _set_timezone_internal_command(engine: Update, context: CallbackContext) -> None:
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
    log_command(engine, _logger)

    if len(context.args) == 0:
        # get timezone
        user_timezone = timezone_service.get_user_timezone(engine.effective_chat.id)
        text = str(user_timezone.tzname(None)) if user_timezone else 'не удалось получить таймзону :('
        send_message(engine.effective_chat.id, text)
    else:
        _set_timezone_internal_command(engine, context)


def help_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine, _logger)
    send_message(engine.effective_chat.id, _get_help_text())


def version_command(engine: Update, context: CallbackContext) -> None:
    log_command(engine, _logger)
    send_message(engine.effective_chat.id, hltv_upcoming_events_bot.__version__)


def send_message(chat_id: int, msg: str):
    bot = telegram.Bot(config.BOT_TOKEN)
    try:
        bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except telegram.error.TelegramError as ex:
        _logger.error(f'failed to send message (chat_id={chat_id}): {ex}')


def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    _logger.error(msg="Exception while handling an update: ", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    # tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    # tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    # update_str = update.to_dict() if isinstance(update, Update) else str(update)
    # message = (
    #     f'An exception was raised while handling an update\n'
    #     f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
    #     '</pre>\n\n'
    #     f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
    #     f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
    #     f'<pre>{html.escape(tb_string)}</pre>'
    # )

    # Finally, send the message
    # context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)


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
    dispatcher.add_handler(CommandHandler("settimezone", set_timezone_command))
    dispatcher.add_handler(CommandHandler("timezone", get_timezone_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("version", version_command))

    dispatcher.add_error_handler(error_handler)

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
