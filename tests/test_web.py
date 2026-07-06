"""Tests for Phase 1 baseline exam web server."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from ssc_study.web import create_app


@pytest.fixture
def web_client(seeded_db):
    """Fixture providing a TestClient configured with seeded_db."""
    app = create_app(seeded_db)
    return TestClient(app)


def test_landing_page_renders(web_client):
    """Verify GET / returns HTML landing page with baseline controls."""
    response = web_client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    
    html = response.text
    assert "Baseline Exam" in html
    assert "btn-smoke" in html
    assert "btn-full" in html


def test_static_assets_served(web_client):
    """Verify static CSS and JS assets are served successfully."""
    css_response = web_client.get("/static/app.css")
    assert css_response.status_code == 200
    assert "text/css" in css_response.headers["content-type"]
    
    js_response = web_client.get("/static/app.js")
    assert js_response.status_code == 200
    assert "application/javascript" in js_response.headers["content-type"] or "text/plain" in js_response.headers["content-type"]


def test_preflight_endpoint(web_client):
    """Verify GET /api/baseline/preflight returns eligibility status."""
    response = web_client.get("/api/baseline/preflight")
    assert response.status_code == 200
    
    data = response.json()
    assert "full_ready" in data
    assert "smoke_ready" in data
    assert "required" in data
    assert "available" in data


def test_start_smoke_exam(web_client):
    """Verify starting smoke exam returns 5 questions with correct section split."""
    response = web_client.post("/api/baseline/start", json={"mode": "smoke"})
    assert response.status_code == 200
    
    data = response.json()
    assert "exam_id" in data
    assert data["mode"] == "smoke"
    assert data["question_count"] == 5
    assert len(data["questions"]) == 5
    
    # Ensure options are returned but not correct labels
    for q in data["questions"]:
        assert "question_id" in q
        assert "options" in q
        assert "correct_option_label" not in q
        assert "correct" not in q


def test_start_invalid_mode(web_client):
    """Verify start returns HTTP 400 for invalid mode."""
    response = web_client.post("/api/baseline/start", json={"mode": "invalid"})
    assert response.status_code == 400


def test_submit_smoke_exam(web_client):
    """Verify submitting smoke exam scores results and persists the session."""
    # First start an exam to get questions
    start_resp = web_client.post("/api/baseline/start", json={"mode": "smoke"})
    assert start_resp.status_code == 200
    start_data = start_resp.json()
    exam_id = start_data["exam_id"]
    exam_token = start_data["exam_token"]
    questions = start_data["questions"]
    
    # Build answers payload
    answers = []
    for idx, q in enumerate(questions):
        answers.append({
            "question_id": q["question_id"],
            "user_answer": "1" if idx % 2 == 0 else "2",
            "time_spent_seconds": 15,
            "marked_for_review": False
        })
        
    payload = {
        "exam_id": exam_id,
        "exam_token": exam_token,
        "mode": "smoke",
        "started_at": "2026-07-06T10:00:00Z",
        "ended_at": "2026-07-06T10:05:00Z",
        "answers": answers
    }
    
    submit_resp = web_client.post("/api/baseline/submit", json=payload)
    assert submit_resp.status_code == 200
    
    submit_data = submit_resp.json()
    assert "session_id" in submit_data
    assert submit_data["mode"] == "smoke"
    assert submit_data["question_count"] == 5
    assert "accuracy" in submit_data
    assert "by_section" in submit_data
    
    # Verify double submit returns same result
    double_resp = web_client.post("/api/baseline/submit", json=payload)
    assert double_resp.status_code == 200
    assert double_resp.json()["session_id"] == submit_data["session_id"]


def test_get_result_detail(web_client):
    """Verify result retrieval endpoint works and includes next_steps."""
    # Submit first to get a real session
    start_resp = web_client.post("/api/baseline/start", json={"mode": "smoke"})
    start_data = start_resp.json()
    exam_id = start_data["exam_id"]
    exam_token = start_data["exam_token"]
    questions = start_data["questions"]
    
    answers = [{
        "question_id": q["question_id"],
        "user_answer": "1",
        "time_spent_seconds": 10,
        "marked_for_review": False
    } for q in questions]
    
    payload = {
        "exam_id": exam_id,
        "exam_token": exam_token,
        "mode": "smoke",
        "started_at": "2026-07-06T10:00:00Z",
        "ended_at": "2026-07-06T10:05:00Z",
        "answers": answers
    }
    
    submit_resp = web_client.post("/api/baseline/submit", json=payload)
    session_id = submit_resp.json()["session_id"]
    
    result_resp = web_client.get(f"/api/baseline/result/{session_id}")
    assert result_resp.status_code == 200
    res_data = result_resp.json()
    assert res_data["session_id"] == session_id
    assert "next_steps" in res_data
    assert res_data["next_steps"]["mode"] == "smoke"
    assert "overall_action" in res_data["next_steps"]


def test_get_result_next_steps_endpoint(web_client):
    """Verify dedicated next-steps endpoint works and returns correct structured schema."""
    start_resp = web_client.post("/api/baseline/start", json={"mode": "smoke"})
    start_data = start_resp.json()
    exam_id = start_data["exam_id"]
    exam_token = start_data["exam_token"]
    questions = start_data["questions"]
    
    answers = [{
        "question_id": q["question_id"],
        "user_answer": "1",
        "time_spent_seconds": 10,
        "marked_for_review": False
    } for q in questions]
    
    payload = {
        "exam_id": exam_id,
        "exam_token": exam_token,
        "mode": "smoke",
        "started_at": "2026-07-06T10:00:00Z",
        "ended_at": "2026-07-06T10:05:00Z",
        "answers": answers
    }
    
    submit_resp = web_client.post("/api/baseline/submit", json=payload)
    session_id = submit_resp.json()["session_id"]
    
    ns_resp = web_client.get(f"/api/baseline/result/{session_id}/next-steps")
    assert ns_resp.status_code == 200
    ns_data = ns_resp.json()
    assert ns_data["session_id"] == session_id
    assert ns_data["mode"] == "smoke"
    assert "overall_action" in ns_data
    assert ns_data["overall_action"]["action_type"] == "smoke_warning"


def test_get_result_next_steps_read_only(web_client, seeded_db):
    """Verify the next-steps endpoint does not mutate DB state."""
    start_resp = web_client.post("/api/baseline/start", json={"mode": "smoke"})
    start_data = start_resp.json()
    answers = [{
        "question_id": q["question_id"],
        "user_answer": "1",
        "time_spent_seconds": 10,
        "marked_for_review": False,
    } for q in start_data["questions"]]
    submit_resp = web_client.post("/api/baseline/submit", json={
        "exam_id": start_data["exam_id"],
        "exam_token": start_data["exam_token"],
        "mode": "smoke",
        "started_at": "2026-07-06T10:00:00Z",
        "ended_at": "2026-07-06T10:05:00Z",
        "answers": answers,
    })
    session_id = submit_resp.json()["session_id"]
    conn = seeded_db.connect()
    before = dict(conn.execute(
        "SELECT ended_at, question_count, correct_count FROM sessions WHERE session_id = ?",
        (session_id,),
    ).fetchone())
    ns_resp = web_client.get(f"/api/baseline/result/{session_id}/next-steps")
    assert ns_resp.status_code == 200
    after = dict(conn.execute(
        "SELECT ended_at, question_count, correct_count FROM sessions WHERE session_id = ?",
        (session_id,),
    ).fetchone())
    assert before == after, "next-steps endpoint mutated session data"

def test_get_result_not_found(web_client):
    """Verify result detail returns HTTP 404 for unknown session ID."""
    response = web_client.get("/api/baseline/result/999999")
    assert response.status_code == 404


def test_landing_page_has_next_steps_div(web_client):
    """Verify GET / returns HTML landing page containing the next steps container."""
    response = web_client.get("/")
    assert response.status_code == 200
    assert "next-steps-content" in response.text


def test_phase3_next_action_endpoint(web_client):
    """Verify that GET /api/phase3/next-action returns a valid schema and works with section filters."""
    response = web_client.get("/api/phase3/next-action")
    assert response.status_code == 200
    data = response.json()
    assert "action_type" in data
    assert "reason" in data
    assert "section" in data
    assert "target_archetype_id" in data
    assert "target_archetype_name" in data
    assert "question_count" in data
    assert "can_start_web_session" in data
    assert "cli_command" in data

    # Test filtering by section
    response_sec = web_client.get("/api/phase3/next-action?section=Quant/DI")
    assert response_sec.status_code == 200
    data_sec = response_sec.json()
    assert "action_type" in data_sec
    assert data_sec["section"] == "Quant/DI" or data_sec["section"] is None
    assert data_sec["cli_command"] == "ssc-study phase3 --section Quant/DI"
    assert "--archetype-id" not in data_sec["cli_command"]
    assert "--probe" not in data_sec["cli_command"]
    assert "--remediation" not in data_sec["cli_command"]
    assert "--boss-fight" not in data_sec["cli_command"]
    assert "--sm2" not in data_sec["cli_command"]


def test_frontend_escapes_phase3_section_action_reason(web_client):
    """Verify section action reasons are escaped before entering result HTML."""
    response = web_client.get("/static/app.js")
    assert response.status_code == 200
    js = response.text
    assert "escapeHtml(ws.action.reason)" in js
    assert "(${ws.action.reason})" not in js


def test_study_summary_endpoint(web_client):
    """Verify that GET /api/study/summary returns a valid schema."""
    response = web_client.get("/api/study/summary")
    assert response.status_code == 200
    data = response.json()
    assert "guardian" in data
    assert "readiness" in data

    guardian = data["guardian"]
    assert "available" in guardian
    assert "mode" in guardian
    assert "total_minutes" in guardian
    assert "mock_recommendation" in guardian
    assert "pulse_recommendation" in guardian
    assert "warnings" in guardian

    readiness = data["readiness"]
    assert "available" in readiness
    assert "status" in readiness
    assert "missing_reasons" in readiness
