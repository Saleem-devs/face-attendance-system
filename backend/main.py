import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.routes.auth import router as auth_router
from backend.routes.students import router as students_router
from backend.routes.attendance import router as attendance_router
from backend.routes.stats import router as stats_router
from backend.config import CORS_ORIGINS
from backend.database import (
    init_sessions_table,
    init_users_table,
    init_students_and_attendance_tables,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_users_table()
    init_sessions_table()
    init_students_and_attendance_tables()
    yield


app = FastAPI(title="Face Attendance API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(students_router)
app.include_router(attendance_router)
app.include_router(stats_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
    CANDIDATE_STATIC_DIRS = [
        os.path.join(BASE_DIR, "web_dashboard", "out"),
        os.path.join(os.path.dirname(BASE_DIR), "Resources", "web_dashboard", "out"),
    ]
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CANDIDATE_STATIC_DIRS = [os.path.join(BASE_DIR, "web_dashboard", "out")]
STATIC_DIR = next((p for p in CANDIDATE_STATIC_DIRS if os.path.exists(p)), None)

if STATIC_DIR and os.path.exists(STATIC_DIR):
    _next_static = os.path.join(STATIC_DIR, "_next", "static")
    if os.path.exists(_next_static):
        app.mount("/_next/static", StaticFiles(directory=_next_static), name="static")

    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="spa")
