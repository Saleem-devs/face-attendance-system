from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from backend.middleware.auth_middleware import get_current_user
from backend.services.attendance_service import (
    get_attendance_by_date,
    get_recent_attendance,
    get_marked_today_ids,
)

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


@router.get("")
def attendance(date: Optional[str] = Query(None), _: dict = Depends(get_current_user)):
    if date:
        return {"data": get_attendance_by_date(date)}
    return {"data": get_recent_attendance(limit=10)}


@router.get("/today/marked")
def attendance_marked_today(_: dict = Depends(get_current_user)):
    return {"data": get_marked_today_ids()}
