from datetime import datetime, timedelta
from backend.database import get_db_connection


def get_attendance_by_date(date_str: str):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, student_id, student_name, attendance_date, attendance_time, timestamp
            FROM attendance
            WHERE attendance_date = ?
            ORDER BY attendance_time DESC
            """,
            (date_str,),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]


def get_recent_attendance(limit: int = 10):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, student_id, student_name, attendance_date, attendance_time, timestamp
            FROM attendance
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]


def get_marked_today_ids():
    today = datetime.now().strftime("%Y-%m-%d")
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT student_id FROM attendance WHERE attendance_date = ?",
            (today,),
        )
        rows = cur.fetchall()
        return [r[0] for r in rows]


def get_today_stats():
    today = datetime.now().strftime("%Y-%m-%d")
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM attendance WHERE attendance_date = ?", (today,)
        )
        present = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM attendance")
        records = cur.fetchone()[0]
        return {"present": present, "records": records}


def get_week_stats(days: int = 7):
    results = []
    with get_db_connection() as conn:
        cur = conn.cursor()
        for i in range(days):
            target = datetime.now().date() - timedelta(days=i)
            date_str = target.strftime("%Y-%m-%d")
            cur.execute(
                "SELECT COUNT(*) FROM attendance WHERE attendance_date = ?", (date_str,)
            )
            present = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM students")
            total = cur.fetchone()[0]
            pct = round((present / total * 100), 2) if total > 0 else 0.0
            results.append(
                {"date": date_str, "marked": present, "total": total, "percentage": pct}
            )
    return list(reversed(results))
