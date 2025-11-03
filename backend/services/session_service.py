import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
from backend.database import get_db_connection, init_sessions_table

SESSION_DURATION_HOURS = 24
SESSION_ID_LENGTH = 32

init_sessions_table()


def generate_session_id() -> str:
    return secrets.token_urlsafe(SESSION_ID_LENGTH)


def create_session(
    user_id: int, username: str, ip_address: str = None, user_agent: str = None
) -> str:
    session_id = generate_session_id()
    now = datetime.now()
    expires_at = now + timedelta(hours=SESSION_DURATION_HOURS)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO sessions (session_id, user_id, username, created_at,expires_at, last_activity, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                user_id,
                username,
                now.isoformat(),
                expires_at.isoformat(),
                now.isoformat(),
                ip_address,
                user_agent,
            ),
        )

    return session_id


def validate_session(session_id: str) -> Optional[Dict]:
    if not session_id:
        return None

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT user_id, username, expires_at, last_activity
            FROM sessions
            WHERE session_id = ?
            """,
            (session_id,),
        )
        row = cursor.fetchone()

        if not row:
            return None

        expires_at = datetime.fromisoformat(row["expires_at"])
        if datetime.now() > expires_at:
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            return None

        cursor.execute(
            """
            UPDATE sessions 
            SET last_activity = ?
            WHERE session_id = ?
            """,
            (datetime.now().isoformat(), session_id),
        )

        return {"user_id": row["user_id"], "username": row["username"]}


def delete_session(session_id: str) -> bool:
    if not session_id:
        return False

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        deleted = cursor.rowcount > 0
        return deleted
