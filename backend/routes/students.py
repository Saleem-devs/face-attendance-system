from fastapi import APIRouter, Depends, HTTPException
from backend.middleware.auth_middleware import get_current_user
from backend.services.student_service import list_students, get_student_by_student_id

router = APIRouter(prefix="/api/students", tags=["Students"])


@router.get("")
def get_students(_: dict = Depends(get_current_user)):
    return {"data": list_students()}


@router.get("/{student_id}")
def get_student(student_id: str, _: dict = Depends(get_current_user)):
    student = get_student_by_student_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"data": student}
