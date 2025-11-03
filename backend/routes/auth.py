from fastapi import APIRouter, HTTPException, Response, Request, Depends
from backend.models import LoginRequest
from backend.services.auth_service import authenticate_user
from backend.services.session_service import delete_session
from backend.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login")
def login(credentials: LoginRequest, response: Response, request: Request):

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    success, session_id, username, message = authenticate_user(
        credentials.username, credentials.password, ip_address, user_agent
    )

    if not success:
        raise HTTPException(status_code=401, detail=message)

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=86400,
    )

    return {"success": True, "message": message, "username": username}


@router.post("/logout")
def logout(response: Response, request: Request):

    session_id = request.cookies.get("session_id")

    if session_id:
        delete_session(session_id)

    response.delete_cookie("session_id")

    return {"success": True, "message": "Logged out successfully"}


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):

    return {"user_id": current_user["user_id"], "username": current_user["username"]}
