from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.db.database import init_db, init_documents_table
from app.route import router

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
STATIC_DIR = BASE_DIR / "frontend" / "static"
UPLOAD_DIR = BASE_DIR / "uploads"

# Create uploads directory
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize FastAPI
app = FastAPI(title="IntelliDocs")

# Configure templates and static files
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)

# Initialize database
init_db()
init_documents_table()

# Register API routes
app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "IntelliDocs"}