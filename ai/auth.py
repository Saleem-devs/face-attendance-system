import sqlite3
import bcrypt
import os
from pathlib import Path

DB_DIR = "db"
DB_PATH = os.path.join(DB_DIR, "attendance.db")

Path(DB_DIR).mkdir(parents=True, exist_ok=True)


def hash_password(password):
    pass_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pass_bytes, salt)


def verify_password(password, password_hash):
    pass_bytes = password.encode("utf-8")
    return bcrypt.checkpw(pass_bytes, password_hash)


def init_auth_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin',
            created_at TEXT NOT NULL
        );
    """
    )

    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        default_password = "admin123"
        password_hash = hash_password(default_password)
        from datetime import datetime

        cur.execute(
            """
            INSERT INTO users (username, password_hash, role, created_at)
            VALUES (?, ?, ?, ?)
        """,
            ("admin", password_hash, "admin", datetime.now().isoformat()),
        )
        conn.commit()

    conn.close()


def authenticate(username, password):
    init_auth_database()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT password_hash, role FROM users WHERE username = ?
    """,
        (username,),
    )
    result = cur.fetchone()
    conn.close()

    if result is None:
        return False, None

    password_hash, role = result
    if verify_password(password, password_hash):
        return True, role
    return False, None


def change_password(username, old_password, new_password):
    if not authenticate(username, old_password)[0]:
        return False, "Current password is incorrect"

    if len(new_password) < 6:
        return False, "New password must be at least 6 characters"

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    new_password_hash = hash_password(new_password)
    cur.execute(
        """
        UPDATE users SET password_hash = ? WHERE username = ?
    """,
        (new_password_hash, username),
    )
    conn.commit()
    conn.close()

    return True, "Password changed successfully"
