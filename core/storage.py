"""История посещений и закладки. Хранятся в простом SQLite файле data/browser.db."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "browser.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute("CREATE TABLE IF NOT EXISTS history (url TEXT, title TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP)")
    con.execute("CREATE TABLE IF NOT EXISTS bookmarks (url TEXT PRIMARY KEY, title TEXT)")
    return con


def add_history(url: str, title: str):
    with _connect() as con:
        con.execute("INSERT INTO history (url, title) VALUES (?, ?)", (url, title))


def get_history(limit: int = 50) -> list[tuple]:
    with _connect() as con:
        return con.execute("SELECT url, title, ts FROM history ORDER BY ts DESC LIMIT ?", (limit,)).fetchall()


def add_bookmark(url: str, title: str):
    with _connect() as con:
        con.execute("INSERT OR REPLACE INTO bookmarks (url, title) VALUES (?, ?)", (url, title))


def get_bookmarks() -> list[tuple]:
    with _connect() as con:
        return con.execute("SELECT url, title FROM bookmarks").fetchall()
