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

    @app.get("/api/phase3/next-action")
    async def api_phase3_next_action(section: str | None = None) -> dict:
        from .phase3 import plan_next_action
        action = plan_next_action(db, section=section)

        action_section = section
        if not action_section and action.target_archetype_id is not None:
            conn = db.connect()
            row = conn.execute(
                "SELECT section FROM questions WHERE archetype_id = ? LIMIT 1",
                (action.target_archetype_id,)
            ).fetchone()
            if row:
                action_section = row["section"]

        cli_cmd = "ssc-study phase3"
        if section:
            cli_cmd = f"{cli_cmd} --section {section}"

        return {
            "action_type": action.action_type,
            "reason": action.reason,
            "section": action_section,
            "target_archetype_id": action.target_archetype_id,
            "target_archetype_name": action.target_archetype_name,
            "question_count": action.question_count,
            "can_start_web_session": False,
            "cli_command": cli_cmd,
        }

    @app.get("/api/study/summary")
    async def api_study_summary() -> dict:
        from .guardian import build_guardian_plan
        from .readiness import compute_readiness

        # Guardian summary
        try:
            plan = build_guardian_plan(db)
            guardian_data = {
                "available": True,
                "mode": plan.audit_mode if plan.audit_mode != "normal" else "planner",
                "total_minutes": plan.total_minutes,
                "mock_recommendation": plan.mock_recommendation,
                "pulse_recommendation": plan.pulse_recommendation,
                "warnings": plan.warnings
            }
        except Exception as e:
            guardian_data = {
                "available": False,
                "mode": "planner",
                "total_minutes": 0,
                "mock_recommendation": "none",
                "pulse_recommendation": "none",
                "warnings": [f"Guardian plan unavailable: {e}"]
            }

        # Readiness summary
        try:
            report = compute_readiness(db)
            readiness_data = {
                "available": True,
                "status": "ready" if report.ready else "not_ready",
                "missing_reasons": report.missing
            }
        except Exception as e:
            readiness_data = {
                "available": False,
                "status": "unavailable",
                "missing_reasons": [f"Readiness check failed: {e}"]
            }

        return {
            "guardian": guardian_data,
            "readiness": readiness_data
        }

    return app
