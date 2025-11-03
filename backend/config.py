import os

DB_DIR = "db"
DB_PATH = os.path.join(DB_DIR, "attendance.db")
SECRET_KEY = "your-secret-key-change-in-production"
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
]
