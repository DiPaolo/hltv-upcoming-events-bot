#!/usr/bin/env python
import datetime
import logging
import os

from telegram import Update, ForceReply, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# включаем логгирование
import config
import db.common
import domain.match
from domain.match_state import get_all_match_state_names
from hltv_parser import get_upcoming_matches

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
    matches = get_upcoming_matches()
    match_str_list = list()
    for match in matches:
        match_str = f"{match.time_utc.hour:02}:{match.time_utc.minute:02} " \
                    f"{'*' * match.stars.value}\t{match.team1.name} - {match.team2.name}" \
                    f" <a href=\"{match.url}\">link</a>"
        match_str_list.append(match_str)

    engine.message.reply_text('Нифига' if len(matches) == 0 else '\n\n'.join(match_str_list), parse_mode=ParseMode.HTML)


# другой обработчик - для команды /help. Когда пользователь вводит /help, вызывается этот код
def help_command(engine: Update, context: CallbackContext) -> None:
    # отправляем какой-то стандартный жестко заданный текст
    # engine.message.reply_text('Помощь!')
    engine.message.reply_text("<b>bold</b>, <strong>bold</strong>"
                              "<i>italic</i>, <em>italic</em>"
                              "<u>underline</u>, <ins>underline</ins>", parse_mode=ParseMode.HTML)


def echo(engine: Update, context: CallbackContext) -> None:
    # вызываем команду отправки сообщения пользователю, используя
    # при это текст сообщения, полученный от пользователя
    engine.message.reply_text(engine.message.text)


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
    dispatcher.add_handler(CommandHandler("help", help_command))

    # говорим обработчику сообений, чтобы он вызывал функцию echo каждый раз,
    # когда пользователь отправляем боту сообщение
    #
    # про параметр 'Filters.text & ~Filters.command' можно пока не заморачиваться;
    # он означает, что функция echo будет вызываться только тогда, когда пользователь
    # ввел именно текст, а не команду; в противном случае, если пользователь введет
    # команду /start или /help, эта функция будет вызвана, что нам не нужно
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # непосредственно старт бота
    engine.start_polling()

    # говорим боту работать, пока не нажмем Ctrl-C или что-то не сломается само :)
    engine.idle()


if __name__ == '__main__':
    # import db.team
    # import db.match
    # import db.match_stars
    # import db.match_state
    # import domain.team
    # import domain.match_stars
    #
    # db.common.init_db(config.DB_FILENAME)
    #
    # for match_state in get_all_match_state_names():
    #     db.match_state.add_match_state(match_state)
    #
    # matches = get_upcoming_matches()
    # for match in matches:
    #     db.match.add_match_from_domain_object(match)

    # # test
    # team1_id = db.team.add_team("MASONIC", "https://www.hltv.org/team/10867/masonic")
    # team2_id = db.team.add_team("Invictus International", "https://www.hltv.org/team/10817/invictus-international")
    # new_match = domain.match.Match(domain.team.Team('Navi'), domain.team.Team('BIG'),
    #                                datetime.datetime.fromtimestamp(1674318600),
    #                                domain.match_stars.MatchStars.THREE,
    #                                domain.match_state.MatchState.FINISHED,
    #                                'https://www.hltv.org/matches/2361205/masonic-vs-invictus-international-thunderpick-bitcoin-series-2')
    # db.match.add_match_from_domain_object(new_match)
    # db.match.add_match(team1_id, team2_id,
    #                    1674318600,
    #                    db.match_stars.MatchStars.FOUR,
    #                    'https://www.hltv.org/matches/2361205/masonic-vs-invictus-international-thunderpick-bitcoin-series-2')

    main()
