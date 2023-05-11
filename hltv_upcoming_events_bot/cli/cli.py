#!/usr/bin/env python
import datetime
import logging
import os
import sys

import click as click

import hltv_upcoming_events_bot.bot as bot_impl
import hltv_upcoming_events_bot.service.db as db_service
import hltv_upcoming_events_bot.service.matches as matches_service
import hltv_upcoming_events_bot.service.tg_notifier as tg_notifier_service
import hltv_upcoming_events_bot.service.news as news_service
from hltv_upcoming_events_bot import config
from hltv_upcoming_events_bot.cli.schedule_thread import ScheduleThread
from hltv_upcoming_events_bot.db import init_db


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
@click.option('--pg-database', default=None, help='PostgreSQL database name')
@click.option('--pg-host', default=None, help='PostgreSQL server host')
@click.option('--pg-port', default=None, help='PostgreSQL server port')
@click.option('--pg-username', default=None, help='PostgreSQL username')
@click.option('--pg-password', default=None, help='PostgreSQL password')
def start(token: str, pg_database: str, pg_host: str, pg_port: str, pg_username: str, pg_password: str):
    if token is not None:
        config.BOT_TOKEN = token

    if config.BOT_TOKEN is None:
        logging.error('Bot token is not set')
        click.echo("ERROR: Bot token is not set. Please specify it via environment variable or specify "
                   "'-t' / '--token' command line argument")
        sys.exit(1)

    if pg_database is not None:
        config.DB_FILENAME = pg_database

    if pg_host is not None:
        config.DB_PG_HOST = pg_host

    if pg_port is not None:
        config.DB_PG_PORT = pg_port

    if pg_username is not None:
        config.DB_PG_USER = pg_username

    if pg_password is not None:
        config.DB_PG_PWD = pg_password

    continuous_thread = ScheduleThread()
    continuous_thread.start()

    # matches_service.init()
    tg_notifier_service.init(bot_impl.send_message)
    init_db(config.DB_FILENAME)

    try:
        bot_impl.start(config.BOT_TOKEN)
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
@click.option('--pg-database', default=None, help='PostgreSQL database name')
@click.option('--pg-host', default=None, help='PostgreSQL server host')
@click.option('--pg-port', default=None, help='PostgreSQL server port')
@click.option('--pg-username', default=None, help='PostgreSQL username')
@click.option('--pg-password', default=None, help='PostgreSQL password')
def start(pg_database: str, pg_host: str, pg_port: str, pg_username: str, pg_password: str):
    if pg_database is not None:
        config.DB_FILENAME = pg_database

    if pg_host is not None:
        config.DB_PG_HOST = pg_host

    if pg_port is not None:
        config.DB_PG_PORT = pg_port

    if pg_username is not None:
        config.DB_PG_USER = pg_username

    if pg_password is not None:
        config.DB_PG_PWD = pg_password

    continuous_thread = ScheduleThread()
    continuous_thread.start()

    init_db(config.DB_FILENAME)
    matches_service.init()


@parser.command(help='Parse only once; do not work in background')
@click.option('--pg-database', default=None, help='PostgreSQL database name')
@click.option('--pg-host', default=None, help='PostgreSQL server host')
@click.option('--pg-port', default=None, help='PostgreSQL server port')
@click.option('--pg-username', default=None, help='PostgreSQL username')
@click.option('--pg-password', default=None, help='PostgreSQL password')
def once(pg_database: str, pg_host: str, pg_port: str, pg_username: str, pg_password: str):
    if pg_database is not None:
        config.DB_FILENAME = pg_database

    if pg_host is not None:
        config.DB_PG_HOST = pg_host

    if pg_port is not None:
        config.DB_PG_PORT = pg_port

    if pg_username is not None:
        config.DB_PG_USER = pg_username

    if pg_password is not None:
        config.DB_PG_PWD = pg_password

    init_db(config.DB_FILENAME)
    matches_service.populate_translations()


@parser.command()
@click.option('--to-date', default=None, type=click.DateTime(formats=["%Y-%m-%d"]), help='Parse news until specified '
                                                                                         'date')
@click.option('--pg-database', default=None, help='PostgreSQL database name')
@click.option('--pg-host', default=None, help='PostgreSQL server host')
@click.option('--pg-port', default=None, help='PostgreSQL server port')
@click.option('--pg-username', default=None, help='PostgreSQL username')
@click.option('--pg-password', default=None, help='PostgreSQL password')
def news(to_date: datetime.datetime, pg_database: str, pg_host: str, pg_port: str, pg_username: str, pg_password: str):
    if pg_database is not None:
        config.DB_FILENAME = pg_database

    if pg_host is not None:
        config.DB_PG_HOST = pg_host

    if pg_port is not None:
        config.DB_PG_PORT = pg_port

    if pg_username is not None:
        config.DB_PG_USER = pg_username

    if pg_password is not None:
        config.DB_PG_PWD = pg_password

    init_db(config.DB_FILENAME)
    news_service.populate_news(to_date if to_date is not None else None)


@click.group()
def admin():
    pass


cli.add_command(admin)


@admin.command()
@click.option('--pg-database', default=None, help='PostgreSQL database name')
@click.option('--pg-host', default=None, help='PostgreSQL server host')
@click.option('--pg-port', default=None, help='PostgreSQL server port')
@click.option('--pg-username', default=None, help='PostgreSQL username')
@click.option('--pg-password', default=None, help='PostgreSQL password')
def users(pg_database: str, pg_host: str, pg_port: str, pg_username: str, pg_password: str):
    if pg_database is not None:
        config.DB_FILENAME = pg_database

    if pg_host is not None:
        config.DB_PG_HOST = pg_host

    if pg_port is not None:
        config.DB_PG_PORT = pg_port

    if pg_username is not None:
        config.DB_PG_USER = pg_username

    if pg_password is not None:
        config.DB_PG_PWD = pg_password

    init_db(config.DB_FILENAME)

    idx = 1
    for u in db_service.get_users():
        print(f'{idx}:\t{u.username} ({u.telegram_id})')
        idx += 1

    print(f'\n'
          f'Total: {idx - 1} users')


@admin.command()
@click.option('--pg-database', default=None, help='PostgreSQL database name')
@click.option('--pg-host', default=None, help='PostgreSQL server host')
@click.option('--pg-port', default=None, help='PostgreSQL server port')
@click.option('--pg-username', default=None, help='PostgreSQL username')
@click.option('--pg-password', default=None, help='PostgreSQL password')
@click.option('-n/--number', default=None)
def recent(pg_database: str, pg_host: str, pg_port: str, pg_username: str, pg_password: str, n: int):
    if pg_database is not None:
        config.DB_FILENAME = pg_database

    if pg_host is not None:
        config.DB_PG_HOST = pg_host

    if pg_port is not None:
        config.DB_PG_PORT = pg_port

    if pg_username is not None:
        config.DB_PG_USER = pg_username

    if pg_password is not None:
        config.DB_PG_PWD = pg_password

    if n is None:
        n = 10

    init_db(config.DB_FILENAME)

    requests = db_service.get_recent_user_requests(n)
    idx = 1
    for r in requests:
        print(f'{idx}:\t{r.telegram_utc_time} user {r.user.telegram_id}: {r.text}')
        idx += 1

    print(f'\n'
          f'Total: {idx - 1} users')


@click.group()
def db():
    pass


@db.command()
@click.option('--pg-database', default=None, help='PostgreSQL database name')
@click.option('--pg-host', default=None, help='PostgreSQL server host')
@click.option('--pg-port', default=None, help='PostgreSQL server port')
@click.option('--pg-username', default=None, help='PostgreSQL username')
@click.option('--pg-password', default=None, help='PostgreSQL password')
def upgrade(pg_database: str, pg_host: str, pg_port: str, pg_username: str, pg_password: str):
    import alembic.config
    import alembic.command

    if pg_database is not None:
        config.DB_FILENAME = pg_database

    if pg_host is not None:
        config.DB_PG_HOST = pg_host

    if pg_port is not None:
        config.DB_PG_PORT = pg_port

    if pg_username is not None:
        config.DB_PG_USER = pg_username

    if pg_password is not None:
        config.DB_PG_PWD = pg_password

    cur_file_dir = os.path.dirname(os.path.realpath(__file__))
    project_root_dir = os.path.abspath(os.path.join(cur_file_dir, '..', '..'))
    alembic_config = alembic.config.Config(os.path.join(project_root_dir, 'alembic.ini'))
    alembic_config.set_main_option('script_location', os.path.join(project_root_dir, 'alembic'))
    alembic.command.upgrade(alembic_config, 'head')


cli.add_command(db)


@click.group()
def news():
    pass


@news.command()
@click.option('--pg-database', default=None, help='PostgreSQL database name')
@click.option('--pg-host', default=None, help='PostgreSQL server host')
@click.option('--pg-port', default=None, help='PostgreSQL server port')
@click.option('--pg-username', default=None, help='PostgreSQL username')
@click.option('--pg-password', default=None, help='PostgreSQL password')
def recent(pg_database: str, pg_host: str, pg_port: str, pg_username: str, pg_password: str):
    if pg_database is not None:
        config.DB_FILENAME = pg_database

    if pg_host is not None:
        config.DB_PG_HOST = pg_host

    if pg_port is not None:
        config.DB_PG_PORT = pg_port

    if pg_username is not None:
        config.DB_PG_USER = pg_username

    if pg_password is not None:
        config.DB_PG_PWD = pg_password

    init_db(config.DB_FILENAME)

    cur_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    news_items = db_service.get_recent_news(datetime.datetime.utcnow() - datetime.timedelta(hours=12), 3)
    idx = 1
    for n in news_items:
        print(f'{idx}:\t{n.date_time_utc.astimezone(cur_timezone)} {n.title} ({n.url})')
        idx += 1


cli.add_command(news)


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
