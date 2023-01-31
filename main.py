#!/usr/bin/env python
import logging
import os
import threading
import time

import schedule
import telegram
from telegram import Update, ForceReply, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# включаем логгирование
import config
import service.tg_notifier
from domain.match_stars import MatchStars
from service.matches import get_upcoming_matches

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


# это обработчики команд (handler-ы). Обычно приниают вот эти два параметра, которые содержат нужный
# контекст, то есть необъодимые для нас переменные (типа, имени пользователя, его ID и так далее), и
# созданный нами движок (об этом ниже)

# вот обработчик команды /start. Когда пользователь вводит /start, вызывается эта функция
# то же самое происходит, если пользователь выберет команду start из списка команд (это
# сделаем позже в BotFather)
def start(engine: Update, context: CallbackContext) -> None:
    # получаем имя пользователя, которое он указал у себя в настройках телеграма,
    # из нашего "движка"
    user = engine.effective_user
    # отправляем нашему пользователю приветственное сообщение
    engine.message.reply_markdown_v2(
        fr'Привет, {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def get_upcoming_matches_command(engine: Update, context: CallbackContext) -> None:
    upcoming_matches_str = service.matches.get_upcoming_matches_str()
    engine.message.reply_text('ничего интересного сегодня :(' if not upcoming_matches_str else upcoming_matches_str, parse_mode=ParseMode.HTML)


def subscribe_command(engine: Update, context: CallbackContext) -> None:
    service.tg_notifier.add_subscriber(engine.effective_chat.id)


# другой обработчик - для команды /help. Когда пользователь вводит /help, вызывается этот код
def help_command(engine: Update, context: CallbackContext) -> None:
    # отправляем какой-то стандартный жестко заданный текст
    # engine.message.reply_text('Помощь!')
    engine.message.reply_text("<b>bold</b>, <strong>bold</strong>"
                              "<i>italic</i>, <em>italic</em>"
                              "<u>underline</u>, <ins>underline</ins>", parse_mode=ParseMode.HTML)


def send_message(chat_id: int, msg: str):
    bot = telegram.Bot(token=os.getenv('DP_TG_BOT_TOKEN'))
    bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.HTML)


def main() -> None:
    # создаем объект фреймворка (библиотеки) для создания телеграм-ботов, с помощью
    # которого мы сможем взаимодействовать с фреймворком, то есть тот связующий объект,
    # через который мы будем общаться со всеми внутренностями (которые делают основную
    # работу по отправке сообщений за нас) фреймворка. Причем, общаться будем в обе стороны:
    # принимать сообщения от него и задавать параметры для него
    #
    # я назвал его engine (движок), чтобы было понятнее. В самой либе (библиотеке, фреймворке)
    # он называется Updater, как видно, что немного запутывает
    engine = Updater(os.getenv('DP_TG_BOT_TOKEN'))

    # получаем объект "передатчика" или обработчика сообщений от нашего движка
    dispatcher = engine.dispatcher

    # тут "связываем" наши команды и соответствующие им обработчики (хендлеры);
    # иногда говорят "повесить коллбэк" (коллбэк это то же самое что и обработчики (они же хендлеры),
    # то есть та функция, которая вызывается в ответ на какое-то событие: callback, то есть
    # call back - дословно, что-то вроде вызвать обратно, то есть наша функция, которую мы передали,
    # вызовется позже в ответ на какое-то событие; в нашем случае они будут вызываться тогда, когда
    # пользователь будет выбирать соответствующие команды
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("matches", get_upcoming_matches_command))
    dispatcher.add_handler(CommandHandler("subscribe", subscribe_command))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # говорим обработчику сообений, чтобы он вызывал функцию echo каждый раз,
    # когда пользователь отправляем боту сообщение
    #
    # про параметр 'Filters.text & ~Filters.command' можно пока не заморачиваться;
    # он означает, что функция echo будет вызываться только тогда, когда пользователь
    # ввел именно текст, а не команду; в противном случае, если пользователь введет
    # команду /start или /help, эта функция будет вызвана, что нам не нужно
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # непосредственно старт бота
    engine.start_polling()

    # говорим боту работать, пока не нажмем Ctrl-C или что-то не сломается само :)
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


if __name__ == '__main__':
    env_debug_val = os.environ.get('DP_TG_BOT_DEBUG')
    if env_debug_val:
        config.DEBUG = _get_env_val_as_bool(env_debug_val)

    app_init()
    service.matches.init()
    service.tg_notifier.init(send_message)

    main()
