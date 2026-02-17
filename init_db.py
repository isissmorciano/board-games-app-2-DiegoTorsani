import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'board_games.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')


def init_db(db_path=DB_PATH, schema_path=SCHEMA_PATH):
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn = sqlite3.connect(db_path)
    conn.executescript(sql)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print('Database created at', DB_PATH)
