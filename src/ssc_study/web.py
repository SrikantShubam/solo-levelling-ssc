"""Phase 1 local web MVP — FastAPI routes for the baseline exam UI."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader

from .baseline_web import (
    SMOKE_REQUIREMENTS,
    SMOKE_TOTAL,
    BaselineWebError,
    get_baseline_preflight,
    get_baseline_next_steps as _get_baseline_next_steps,
)
from .baseline_web import get_baseline_result as _get_baseline_result
from .baseline_web import start_baseline_exam as _start_baseline_exam
from .baseline_web import submit_baseline_exam as _submit_baseline_exam
from .db import Database


def start_baseline_exam(db: Database, mode: str) -> dict:
    """Start a baseline exam, translating domain errors to HTTP 400."""
    try:
        return _start_baseline_exam(db, mode)
    except BaselineWebError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def submit_baseline_exam(db: Database, payload: dict) -> dict:
    """Submit a baseline exam, translating domain errors to HTTP 400."""
    try:
        return _submit_baseline_exam(db, payload)
    except BaselineWebError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def get_baseline_result(db: Database, session_id: int) -> dict:
    """Fetch a baseline result, translating missing sessions to HTTP 404."""
    try:
        return _get_baseline_result(db, session_id)
    except BaselineWebError as exc:
        message = str(exc)
        status = 404 if "not found" in message.lower() else 400
        raise HTTPException(status_code=status, detail=message) from exc


def get_baseline_next_steps(db: Database, session_id: int) -> dict:
    """Fetch a baseline next-step recommendation, translating errors to HTTP statuses."""
    try:
        return _get_baseline_next_steps(db, session_id)
    except BaselineWebError as exc:
        message = str(exc)
        status = 404 if "not found" in message.lower() else 400
        raise HTTPException(status_code=status, detail=message) from exc


def create_app(db: Database, templates_dir: str | Path | None = None) -> FastAPI:
    """Build the FastAPI application wired to the given Database."""
    if templates_dir is None:
        templates_dir = Path(__file__).resolve().parent / "templates"

    env = Environment(loader=FileSystemLoader(str(templates_dir)), autoescape=True)

    app = FastAPI(title="SSC Study — Phase 1 MVP")

    static_dir = Path(__file__).resolve().parent / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def landing_page(request: Request) -> str:
        preflight = get_baseline_preflight(db)
        template = env.get_template("landing.html")
        return template.render(
            db_path=str(db.path),
            full_ready=preflight["full_ready"],
            smoke_ready=preflight["smoke_ready"],
            required=preflight["required"],
            available=preflight["available"],
            missing=preflight["missing"],
        )

    @app.get("/api/baseline/preflight")
    async def api_preflight() -> dict:
        return get_baseline_preflight(db)

    @app.post("/api/baseline/start")
    async def api_start(payload: dict) -> dict:
        mode = payload.get("mode")
        if mode not in ("smoke", "full"):
            raise HTTPException(status_code=400, detail=f"Invalid mode: {mode!r}")
        return start_baseline_exam(db, mode)

    @app.post("/api/baseline/submit")
    async def api_submit(payload: dict) -> dict:
        return submit_baseline_exam(db, payload)

    @app.get("/api/baseline/result/{session_id}")
    async def api_result(session_id: int) -> dict:
        return get_baseline_result(db, session_id)

    @app.get("/api/baseline/result/{session_id}/next-steps")
    async def api_result_next_steps(session_id: int) -> dict:
        return get_baseline_next_steps(db, session_id)

    return app