import logging
import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base

import config

engine = Optional[Engine]
Base = declarative_base()


def init_db(name: str):
    global engine

    db_folder = os.path.join(config.OUT_BASE_FOLDER, config.OUT_DB_FOLDER)
    db_filename = os.path.join(db_folder, f'{name}.db')
    db_abs_filename = os.path.abspath(db_filename)
    db_abs_filename = db_abs_filename.replace('\\', '/')

    os.makedirs(db_folder, exist_ok=True)

    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.INFO)

    engine = create_engine(f"sqlite:///{db_abs_filename}"
                           , echo=True,
                           # , future=True
                           )

    # Base.metadata.create_all(engine)


def get_engine():
    return engine
