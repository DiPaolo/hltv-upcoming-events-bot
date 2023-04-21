DEBUG = False
BOT_TOKEN = None  # None means it will be taken from command line; it will be set if appropriate env variable is set

# parsing
BASE_URL = 'https://www.hltv.org'  # no trailing slash

# database
DB_USE_DB = True
DB_USE_SQLITE = False
DB_FILENAME = 'hltv_events'  # used as a database name for Postgres
if DB_USE_SQLITE:
    # makes sense for SQLite only
    OUT_BASE_FOLDER = '.'
    OUT_DB_FOLDER = 'db'
else:
    # the other option is Postgres
    DB_PG_HOST = 'localhost'
    DB_PG_PORT = '5432'
    DB_PG_USER = 'postgres'
    DB_PG_PWD = '123456'
    # DB_PG_DATABASE_NAME = 'hltv_events'
