import bcrypt
from backend.database import get_db_connection
from backend.services.session_service import create_session


def hash_password(password: str) -> bytes:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt)


def verify_password(password: str, password_hash) -> bool:
    password_bytes = password.encode("utf-8")
    hash_bytes = (
        password_hash
        if isinstance(password_hash, (bytes, bytearray))
        else str(password_hash).encode("utf-8")
    )
    return bcrypt.checkpw(password_bytes, hash_bytes)


def authenticate_user(
    username: str, password: str, ip_address: str = None, user_agent: str = None
) -> tuple:

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, username, password_hash, role
            FROM users
            WHERE username = ?
            """,
            (username,),
        )

        row = cursor.fetchone()

        if not row:
            return False, None, None, "Invalid username or password"

        user_id = row["id"]
        username = row["username"]
        stored_hash = row["password_hash"]

        if not verify_password(password, stored_hash):
            return False, None, None, "Invalid username or password"

        session_id = create_session(user_id, username, ip_address, user_agent)

        return True, session_id, username, "Login successful"
