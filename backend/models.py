from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[int] = None
    username: Optional[str] = None


class Student(BaseModel):
    id: int
    student_id: str
    name: str
    email: Optional[str] = None
    department: Optional[str] = None
    is_active: int


class AttendanceRecord(BaseModel):
    id: int
    student_id: str
    name: str
    time_in: str
    status: str
    confidence: Optional[float] = None


class DateStatsResponse(BaseModel):
    date: str
    total_students: int
    present_count: int
    absent_count: int
    attendance_rate: float
    present_students: List[AttendanceRecord]
    absent_students: List[dict]
