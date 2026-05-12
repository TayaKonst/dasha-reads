import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # Must be first — database.py reads DATABASE_URL at import time

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from routers import exercises, sessions, stats  # noqa: E402

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Русский для Даши")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exercises.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(stats.router, prefix="/api")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/stats")
async def stats_page():
    return FileResponse(str(STATIC_DIR / "stats.html"))
