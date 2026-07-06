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


def test_get_result_not_found(web_client):
    """Verify result detail returns HTTP 404 for unknown session ID."""
    response = web_client.get("/api/baseline/result/999999")
    assert response.status_code == 404


def test_landing_page_has_next_steps_div(web_client):
    """Verify GET / returns HTML landing page containing the next steps container."""
    response = web_client.get("/")
    assert response.status_code == 200
    assert "next-steps-content" in response.text
