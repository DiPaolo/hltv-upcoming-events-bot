DEBUG = False

# parsing
BASE_URL = 'https://www.hltv.org'  # no trailing slash

# database
USE_SQLITE = False
DB_FILENAME = 'hltv_events'  # used as a database name for Postgres
if USE_SQLITE:
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
