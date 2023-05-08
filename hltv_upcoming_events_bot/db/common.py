import logging
import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base

from hltv_upcoming_events_bot import config

engine = Optional[Engine]
Base = declarative_base()


def get_db_url(db_name: str) -> str:
    if config.DB_USE_SQLITE:
        db_folder = os.path.join(config.OUT_BASE_FOLDER, config.OUT_DB_FOLDER)
        db_filename = os.path.join(db_folder, f'{db_name}.db')
        db_abs_filename = os.path.abspath(db_filename)
        db_abs_filename = db_abs_filename.replace('\\', '/')

        os.makedirs(db_folder, exist_ok=True)

        logging.basicConfig()
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

        return f'sqlite:///{db_abs_filename}'
    else:
        return f'postgresql://{config.DB_PG_USER}:{config.DB_PG_PWD}@{config.DB_PG_HOST}:{config.DB_PG_PORT}/{db_name}'


def init_db(name: str):
    global engine

    engine = create_engine(get_db_url(name),
                           # , echo=True,
                           # , future=True
                           connect_args={"options": "-c timezone=utc"})
    # Base.metadata.create_all(engine)


def get_engine():
    return engine
