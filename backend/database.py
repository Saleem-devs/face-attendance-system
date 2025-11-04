import sqlite3
import os
import sys
from contextlib import contextmanager

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_DIR = os.path.join(BASE_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "attendance.db")


@contextmanager
def get_db_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def get_db_cursor(conn):
    return conn.cursor()


def init_sessions_table():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = get_db_cursor(conn)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            last_activity TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_session_id ON sessions(session_id)
    """
    )

    conn.commit()
    conn.close()


def init_users_table():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = get_db_cursor(conn)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin',
            created_at TEXT NOT NULL
        )
    """
    )

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        from datetime import datetime

        try:
            import bcrypt

            password_bytes = "admin123".encode("utf-8")
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password_bytes, salt).decode("utf-8")
        except Exception:
            password_hash = "admin123"

        cursor.execute(
            """
            INSERT INTO users (username, password_hash, role, created_at)
            VALUES (?, ?, ?, ?)
            """,
            ("admin", password_hash, "admin", datetime.now().isoformat()),
        )

    conn.commit()
    conn.close()


def init_students_and_attendance_tables():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = get_db_cursor(conn)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_id TEXT UNIQUE NOT NULL,
            email TEXT,
            photo_path TEXT,
            encoding_path TEXT,
            date_registered TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            student_name TEXT NOT NULL,
            attendance_date TEXT NOT NULL,
            attendance_time TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        """
    )

    conn.commit()
    conn.close()
