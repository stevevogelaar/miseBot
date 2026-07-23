"""miseBot SQLite database layer."""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "misebot.db"


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK(type IN ('shopping', 'prep')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'sent', 'archived')),
            sent_at TIMESTAMP,
            ttl_days INTEGER DEFAULT 7,
            expires_at TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS list_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            list_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            quantity TEXT,
            unit TEXT,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'done')),
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            done_at TIMESTAMP,
            FOREIGN KEY (list_id) REFERENCES lists(id) ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT,
            default_unit TEXT,
            is_sub_ingredient INTEGER DEFAULT 0,
            usage_rate_per_week REAL,
            current_stock REAL,
            min_stock REAL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY DEFAULT 1,
            email_to TEXT,
            email_from TEXT,
            smtp_host TEXT,
            smtp_port INTEGER DEFAULT 587,
            smtp_user TEXT,
            smtp_pass TEXT,
            list_ttl_days INTEGER DEFAULT 7,
            active_user TEXT DEFAULT 'Brianne'
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS time_blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT NOT NULL,
            planned_start TEXT,
            planned_end TEXT,
            actual_start TEXT,
            actual_end TEXT,
            items TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT NOT NULL,
            trigger_time TEXT,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'triggered', 'dismissed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            prep_items TEXT
        )
        """
    )

    # Default settings row
    cursor.execute(
        "INSERT OR IGNORE INTO settings (id, email_to, email_from, active_user) VALUES (1, '', '', 'Brianne')"
    )

    conn.commit()
    conn.close()


def get_or_create_list(list_type: str, ttl_days: int = 7):
    conn = get_conn()
    cursor = conn.cursor()

    # Check for active list of this type
    cursor.execute(
        "SELECT * FROM lists WHERE type = ? AND status = 'active' ORDER BY created_at DESC LIMIT 1",
        (list_type,),
    )
    row = cursor.fetchone()

    if row:
        conn.close()
        return dict(row)

    # Create new list
    expires = datetime.now() + timedelta(days=ttl_days)
    cursor.execute(
        "INSERT INTO lists (type, ttl_days, expires_at) VALUES (?, ?, ?)",
        (list_type, ttl_days, expires.isoformat()),
    )
    list_id = cursor.lastrowid
    conn.commit()

    cursor.execute("SELECT * FROM lists WHERE id = ?", (list_id,))
    new_row = cursor.fetchone()
    conn.close()
    return dict(new_row)


def add_item(list_id: int, name: str, quantity: str = "", unit: str = ""):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO list_items (list_id, name, quantity, unit) VALUES (?, ?, ?, ?)",
        (list_id, name, quantity, unit),
    )
    item_id = cursor.lastrowid
    conn.commit()
    cursor.execute("SELECT * FROM list_items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)


def get_items(list_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM list_items WHERE list_id = ? ORDER BY added_at",
        (list_id,),
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def mark_done(item_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE list_items SET status = 'done', done_at = ? WHERE id = ?",
        (datetime.now().isoformat(), item_id),
    )
    conn.commit()
    conn.close()


def mark_pending(item_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE list_items SET status = 'pending', done_at = NULL WHERE id = ?",
        (item_id,),
    )
    conn.commit()
    conn.close()


def remove_item(item_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM list_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


def archive_old_lists(ttl_days: int = 30):
    conn = get_conn()
    cursor = conn.cursor()
    cutoff = (datetime.now() - timedelta(days=ttl_days)).isoformat()
    cursor.execute(
        "UPDATE lists SET status = 'archived' WHERE status = 'active' AND created_at < ?",
        (cutoff,),
    )
    conn.commit()
    conn.close()


def get_settings():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM settings WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}


def save_settings(**kwargs):
    conn = get_conn()
    cursor = conn.cursor()
    cols = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values())
    cursor.execute(f"UPDATE settings SET {cols} WHERE id = 1", vals)
    conn.commit()
    conn.close()


def add_time_block(label: str, planned_start: str, planned_end: str, items: list = None):
    conn = get_conn()
    cursor = conn.cursor()
    items_json = json.dumps(items or [])
    cursor.execute(
        "INSERT INTO time_blocks (label, planned_start, planned_end, items) VALUES (?, ?, ?, ?)",
        (label, planned_start, planned_end, items_json),
    )
    block_id = cursor.lastrowid
    conn.commit()
    cursor.execute("SELECT * FROM time_blocks WHERE id = ?", (block_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)


def get_time_blocks():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM time_blocks ORDER BY planned_start")
    rows = [dict(r) for r in cursor.fetchall()]
    for r in rows:
        r["items"] = json.loads(r["items"] or "[]")
    conn.close()
    return rows


def add_reminder(label: str, trigger_time: str):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reminders (label, trigger_time) VALUES (?, ?)",
        (label, trigger_time),
    )
    rid = cursor.lastrowid
    conn.commit()
    cursor.execute("SELECT * FROM reminders WHERE id = ?", (rid,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)


def get_reminders(status: str = "pending"):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM reminders WHERE status = ? ORDER BY trigger_time",
        (status,),
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def dismiss_reminder(reminder_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE reminders SET status = 'dismissed' WHERE id = ?",
        (reminder_id,),
    )
    conn.commit()
    conn.close()


def get_ingredients():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ingredients ORDER BY name")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def seed_ingredients(ingredients: list):
    conn = get_conn()
    cursor = conn.cursor()
    for ing in ingredients:
        cursor.execute(
            """
            INSERT OR IGNORE INTO ingredients
            (name, category, default_unit, is_sub_ingredient, usage_rate_per_week, current_stock, min_stock)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ing["name"],
                ing.get("category", ""),
                ing.get("default_unit", ""),
                ing.get("is_sub_ingredient", 0),
                ing.get("usage_rate_per_week", 0),
                ing.get("current_stock", 0),
                ing.get("min_stock", 0),
            ),
        )
    conn.commit()
    conn.close()


def seed_menu_items(items: list):
    conn = get_conn()
    cursor = conn.cursor()
    for item in items:
        cursor.execute(
            "INSERT OR IGNORE INTO menu_items (name, prep_items) VALUES (?, ?)",
            (item["name"], json.dumps(item.get("prep_items", []))),
        )
    conn.commit()
    conn.close()


def get_menu_items():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu_items ORDER BY name")
    rows = [dict(r) for r in cursor.fetchall()]
    for r in rows:
        r["prep_items"] = json.loads(r["prep_items"] or "[]")
    conn.close()
    return rows
