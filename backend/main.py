from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.auth import router as auth_router
from backend.routes.students import router as students_router
from backend.routes.attendance import router as attendance_router
from backend.routes.stats import router as stats_router
from backend.config import CORS_ORIGINS

app = FastAPI(title="Face Attendance API", version="1.0.0")

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
