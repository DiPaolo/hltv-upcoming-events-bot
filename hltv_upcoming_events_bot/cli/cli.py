#!/usr/bin/env python

import logging
import os
import sys

import click as click

import hltv_upcoming_events_bot.bot as bot_impl
import hltv_upcoming_events_bot.db as db
import hltv_upcoming_events_bot.service.matches as matches_service
import hltv_upcoming_events_bot.service.tg_notifier as tg_notifier_service
from hltv_upcoming_events_bot import config
from hltv_upcoming_events_bot.cli.schedule_thread import ScheduleThread
from hltv_upcoming_events_bot.db.user import get_users
from hltv_upcoming_events_bot.db.user_request import get_recent_user_requests


@click.group()
@click.option('--debug/--no-debug', default=None)
def cli(debug: bool):
    # apply env variables first;
    # command line parameters have higher priority, so it goes after

    _apply_env_variables_to_config()

    if debug is not None:
        config.DEBUG_PRINT = debug


@click.group()
def bot():
    pass


cli.add_command(bot)


@bot.command()
@click.option('-t', '--token', default=None, help='Bot token')
def start(token: str):
    if token is None:
        if config.BOT_TOKEN is None:
            logging.error('Bot token is not set')
            click.echo("ERROR: Bot token is not set. Please specify it via environment variable or specify "
                       "'-t' / '--token' command line argument")
            sys.exit(1)

        token = config.BOT_TOKEN

    continuous_thread = ScheduleThread()
    continuous_thread.start()

    # matches_service.init()
    tg_notifier_service.init(bot_impl.send_message)

    db.init_db(config.DB_FILENAME)

    try:
        bot_impl.start(token)
    except KeyboardInterrupt:
        logging.info('Keyboard interrupt. Successfully exiting application')
        sys.exit(0)
    except Exception as ex:
        logging.critical(f'Exiting application: {ex}')
        sys.exit(1)


@click.group()
def parser():
    pass


cli.add_command(parser)


@parser.command()
def start():
    continuous_thread = ScheduleThread()
    continuous_thread.start()

    db.init_db(config.DB_FILENAME)
    matches_service.init()

    # try:
    #     bot_impl.start(token)
    # except KeyboardInterrupt:
    #     logging.info('Keyboard interrupt. Successfully exiting application')
    #     sys.exit(0)
    # except Exception as ex:
    #     logging.critical(f'Exiting application: {ex}')
    #     sys.exit(1)


@click.group()
def admin():
    pass


cli.add_command(admin)


@admin.command()
def users():
    db.init_db(config.DB_FILENAME)

    users = get_users()
    idx = 1
    for u in users:
        print(f'{idx}:\t{u.username} ({u.telegram_id})')
        idx += 1

    print(f'\n'
          f'Total: {idx - 1} users')


@admin.command()
@click.option('-n/--number', default=None)
def recent(n: int):
    if n is None:
        n = 10

    db.init_db(config.DB_FILENAME)

    requests = get_recent_user_requests(n)
    idx = 1
    for r in requests:
        print(f'{idx}:\t{r.telegram_utc_time} user {r.user_id}: {r.text}')
        idx += 1

    print(f'\n'
          f'Total: {idx - 1} users')


def init_app():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def _get_env_val_as_bool(val) -> bool:
    return val if type(val) == bool else val.lower() in ['true', 'yes', '1']


def _apply_env_variables_to_config():
    env_debug_val = os.environ.get('DP_TG_BOT_DEBUG')
    if env_debug_val:
        config.DEBUG = _get_env_val_as_bool(env_debug_val)

    env_token_val = os.environ.get('DP_TG_BOT_TOKEN')
    if env_token_val:
        config.BOT_TOKEN = env_token_val

    # env_check_ssl_cert = os.environ.get('DP_TG_BOT_CHECK_SSL_CERT')
    # if env_check_ssl_cert:
    #     config.CHECK_SSL_CERT = _get_env_val_as_bool(env_check_ssl_cert)
    #
    # dadata_token = os.environ.get('DP_TG_BOT_DADATA_TOKEN')
    # if dadata_token:
    #     config.DADATA_TOKEN = dadata_token
    #
    # dadata_secret = os.environ.get('DP_TG_BOT_DADATA_SECRET')
    # if dadata_secret:
    #     config.DADATA_SECRET = dadata_secret
