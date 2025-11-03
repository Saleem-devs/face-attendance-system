from backend.database import get_db_connection


def list_students():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, student_id, name, COALESCE(email,'' ) AS email, COALESCE(date_registered,'') AS date_registered
            FROM students
            WHERE 1=1
            ORDER BY date_registered ASC
            """
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]


def get_student_by_student_id(student_id: str):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, student_id, name, COALESCE(email,'' ) AS email, COALESCE(date_registered,'') AS date_registered
            FROM students
            WHERE student_id = ?
            """,
            (student_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def count_students() -> int:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM students")
        return cur.fetchone()[0]
