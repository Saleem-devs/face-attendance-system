from fastapi import APIRouter, Depends
from backend.middleware.auth_middleware import get_current_user
from backend.services.attendance_service import get_today_stats, get_week_stats
from backend.services.student_service import count_students

router = APIRouter(prefix="/api/stats", tags=["Stats"])


@router.get("")
def stats(_: dict = Depends(get_current_user)):
    totals = count_students()
    today = get_today_stats()
    rate = round((today["present"] / totals * 100), 2) if totals > 0 else 0.0
    return {
        "total_students": totals,
        "marked_today": today["present"],
        "attendance_rate_today": rate,
        "total_attendance_records": today["records"],
    }


@router.get("/weekly")
def weekly(_: dict = Depends(get_current_user)):
    return {"data": get_week_stats(days=7)}
