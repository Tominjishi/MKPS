import sqlite3
DB_FILE = 'data/data.db'


create_statements = [
    """CREATE TABLE IF NOT EXISTS release (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        format_id INTEGER NOT NULL,
        type_id INTEGER NOT NULL,
        release_group_mbid TEXT,
        title TEXT NOT NULL,
        release_date TEXT,
        artist_credit_phrase TEXT NOT NULL,
        cover BLOB,
        added_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(format_id) REFERENCES format(id) ON DELETE CASCADE,
        FOREIGN KEY(type_id) REFERENCES release_type(id) ON DELETE CASCADE
    );""",

    """CREATE TABLE IF NOT EXISTS artist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mbid TEXT,
        name TEXT NOT NULL,
        type TEXT NOT NULL
    );""",

    """CREATE TABLE IF NOT EXISTS artist_release (
        release_id INTEGER NOT NULL,
        artist_id INTEGER NOT NULL,
        FOREIGN KEY(release_id) REFERENCES release(id) ON DELETE CASCADE,
        FOREIGN KEY(artist_id) REFERENCES artist(id) ON DELETE CASCADE,
        PRIMARY KEY (release_id, artist_id)
    );""",

    """CREATE TABLE IF NOT EXISTS genre (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mbid TEXT UNIQUE,
        name TEXT NOT NULL UNIQUE
    );""",

    """CREATE TABLE IF NOT EXISTS release_genre (
        genre_id INTEGER NOT NULL,
        release_id INTEGER NOT NULL,
        vote_count INTEGER,
        FOREIGN KEY(genre_id) REFERENCES genre(id) ON DELETE CASCADE,
        FOREIGN KEY(release_id) REFERENCES release(id) ON DELETE CASCADE
        PRIMARY KEY (genre_id, release_id)
    );""",

    """CREATE TABLE IF NOT EXISTS artist_genre (
        genre_id INTEGER NOT NULL,
        artist_id INTEGER NOT NULL,
        vote_count INTEGER,
        FOREIGN KEY(genre_id) REFERENCES genre(id) ON DELETE CASCADE,
        FOREIGN KEY(artist_id) REFERENCES artist(id) ON DELETE CASCADE,
        PRIMARY KEY (genre_id, artist_id)
    );""",

    """CREATE TABLE IF NOT EXISTS format (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );""",

    """CREATE TABLE IF NOT EXISTS release_type (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );""",

    """CREATE TABLE IF NOT EXISTS track (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        release_id INTEGER NOT NULL,
        actual_position INTEGER NOT NULL,
        position INTEGER NOT NULL,
        title TEXT NOT NULL,
        length INTEGER NOT NULL,
        FOREIGN KEY(release_id) REFERENCES release(id) ON DELETE CASCADE
    );"""
]

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        for statement in create_statements:
            cursor.execute(statement)
        conn.commit()