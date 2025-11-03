import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "web_dashboard", "out")

if os.path.exists(STATIC_DIR):
    _next_static = os.path.join(STATIC_DIR, "_next", "static")
    if os.path.exists(_next_static):
        app.mount("/_next/static", StaticFiles(directory=_next_static), name="static")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="Not found")

        if full_path.startswith("_next/"):
            return {"error": "Not found"}, 404

        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)

        index_path = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)

        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Not found")
