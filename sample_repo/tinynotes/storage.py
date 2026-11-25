"""笔记的存储层。用标准库的 sqlite3，没有 ORM。"""
import sqlite3
from datetime import datetime, timezone

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL,
    body       TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


def connect(path: str | None = None) -> sqlite3.Connection:
    """打开数据库，表不存在就建表。path 不传时用 config.DB_PATH。"""
    conn = sqlite3.connect(path or config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    return conn


def _to_dict(row: sqlite3.Row | None) -> dict | None:
    return dict(row) if row is not None else None


def add_note(conn: sqlite3.Connection, title: str, body: str) -> int:
    """新增一条笔记，返回它的 id。"""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    cur = conn.execute(
        "INSERT INTO notes (title, body, created_at) VALUES (?, ?, ?)",
        (title, body, now),
    )
    conn.commit()
    return cur.lastrowid


def get_note(conn: sqlite3.Connection, note_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    return _to_dict(row)


def list_notes(conn: sqlite3.Connection, page: int = 1) -> list[dict]:
    """按 id 倒序分页列出笔记，每页 config.PAGE_SIZE 条，page 从 1 开始。"""
    offset = (max(page, 1) - 1) * config.PAGE_SIZE
    rows = conn.execute(
        "SELECT * FROM notes ORDER BY id DESC LIMIT ? OFFSET ?",
        (config.PAGE_SIZE, offset),
    ).fetchall()
    return [dict(r) for r in rows]


def delete_note(conn: sqlite3.Connection, note_id: int) -> bool:
    """删除一条笔记。笔记不存在时返回 False。"""
    cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    return cur.rowcount > 0


def search_notes(conn: sqlite3.Connection, keyword: str) -> list[dict]:
    """在标题和正文里做子串匹配（SQL 的 LIKE），不分词。"""
    pattern = f"%{keyword}%"
    rows = conn.execute(
        "SELECT * FROM notes WHERE title LIKE ? OR body LIKE ? ORDER BY id DESC",
        (pattern, pattern),
    ).fetchall()
    return [dict(r) for r in rows]
