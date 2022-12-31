import sqlite3
import config


def connect_sqlite(path_to_db):
    return sqlite3.connect(database=path_to_db)
