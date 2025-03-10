import sqlite3

DB_FILE = "data/data.db"

create_statements = [
    """CREATE TABLE IF NOT EXISTS collection_entry(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        release_group_mbid TEXT NOT NULL,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        release_date TEXT,
        format TEXT NOT NULL,
        artist_credit_phrase TEXT NOT NULL,
        cover BLOB,
        added_at TEXT DEFAULT CURRENT_TIMESTAMP
    );""",

    """CREATE TABLE IF NOT EXISTS artist(
        mbid TEXT PRIMARY KEY,
        type TEXT,
        name TEXT NOT NULL
    );""",

    """CREATE TABLE IF NOT EXISTS artist_entry_link(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        collection_entry_id INTEGER NOT NULL,
        artist_mbid TEXT NOT NULL,
        FOREIGN KEY(collection_entry_id) REFERENCES collection_entry(id) ON DELETE CASCADE,
        FOREIGN KEY(artist_mbid) REFERENCES artist(mbid) ON DELETE CASCADE
    );""",

    """CREATE TABLE IF NOT EXISTS genre(
        mbid TEXT PRIMARY KEY,
        name TEXT NOT NULL
    );""",

    """CREATE TABLE IF NOT EXISTS genre_link (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        genre_mbid TEXT NOT NULL,
        vote_count INTEGER NOT NULL,
        collection_entry_id INTEGER,
        artist_mbid TEXT,
        FOREIGN KEY(collection_entry_id) REFERENCES collection_entry(id) ON DELETE CASCADE,
        FOREIGN KEY(genre_mbid) REFERENCES genre(mbid) ON DELETE CASCADE,
        FOREIGN KEY(artist_mbid) REFERENCES artist(mbid) ON DELETE CASCADE
    );""",

    """CREATE TABLE IF NOT EXISTS track (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number INTEGER NOT NULL,
        title TEXT NOT NULL,
        length INTEGER NOT NULL,
        collection_entry_id INTEGER NOT NULL,
        FOREIGN KEY(collection_entry_id) REFERENCES collection_entry(id) ON DELETE CASCADE
    );"""
]

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        for statement in create_statements:
            cursor.execute(statement)
        conn.commit()