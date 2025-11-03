from fastapi import Request, HTTPException, status
from backend.services.session_service import validate_session
from typing import Optional


async def get_current_user(request: Request) -> dict:
    session_id = request.cookies.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    user = validate_session(session_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired user"
        )

    return user
