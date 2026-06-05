"""Tests for the quiz session engine."""

from __future__ import annotations

from io import StringIO

from rich.console import Console

from ssc_study.quiz import QuizSession, _load_questions


class TestQuizSession:
    """QuizSession state machine tests."""

    def test_start_creates_session(self, seeded_db):
        """start() creates a session row and returns Session."""
        console = Console(file=StringIO(), force_terminal=True, width=80)
        qs = QuizSession(
            db=seeded_db,
            session_type="mock",
            question_count=5,
            console=console,
        )
        session = qs.start()

        assert session.session_id is not None
        assert session.session_type == "mock"
        assert session.question_count == 5

        # Verify persisted in DB
        conn = seeded_db.connect()
        row = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?",
            (session.session_id,),
        ).fetchone()
        assert row is not None
        assert row["session_type"] == "mock"

    def test_has_next_initial(self, seeded_db):
        """has_next returns True after start when questions exist."""
        console = Console(file=StringIO(), force_terminal=True, width=80)
        qs = QuizSession(
            db=seeded_db,
            session_type="mock",
            question_count=5,
            console=console,
        )
        qs.start()
        assert qs.has_next() is True

    def test_has_next_after_full(self, seeded_db):
        """has_next returns False when all questions answered."""
        console = Console(file=StringIO(), force_terminal=True, width=80)
        qs = QuizSession(
            db=seeded_db,
            session_type="mock",
            question_count=2,
            console=console,
        )

        # Override questions to avoid DB dependency in present_next
        # (which would block on actual user input)
        from ssc_study.models import Question, Option
        qs.questions = [
            Question(
                question_id="test1", pdf_name="test", source_page=1,
                global_question_number=1, section="Quant/DI", year=2021,
                tier="tier1", question_text="Test?", correct_option_label="1",
                options=[Option("1", "A"), Option("2", "B"), Option("3", "C"), Option("4", "D")],
            ),
            Question(
                question_id="test2", pdf_name="test", source_page=1,
                global_question_number=2, section="Reasoning", year=2021,
                tier="tier1", question_text="Test2?", correct_option_label="2",
                options=[Option("1", "A"), Option("2", "B"), Option("3", "C"), Option("4", "D")],
            ),
        ]
        qs.start = lambda: None  # type: ignore[method-assign]
        qs.session = type("obj", (object,), {"session_id": 1})()

        for _ in range(2):
            assert qs.has_next() is True
            qs.current_index += 1
        assert qs.has_next() is False

    def test_abort_sets_flag(self, seeded_db):
        """abort marks the session as abandoned."""
        console = Console(file=StringIO(), force_terminal=True, width=80)
        qs = QuizSession(
            db=seeded_db,
            session_type="mock",
            question_count=5,
            console=console,
        )
        qs.session = type("obj", (object,), {"session_id": 1, "started_at": "2025-01-01"})()
        qs.abort()
        assert qs._aborted is True

    def test_finish_empty_returns_none(self, seeded_db):
        """finish returns None if no session started."""
        console = Console(file=StringIO(), force_terminal=True, width=80)
        qs = QuizSession(
            db=seeded_db,
            session_type="mock",
            question_count=5,
            console=console,
        )
        result = qs.finish()
        assert result is None

    def test_finish_updates_session(self, seeded_db):
        """finish() sets ended_at and computes correct_count."""
        conn = seeded_db.connect()
        conn.execute(
            "INSERT INTO sessions (session_type, started_at) VALUES ('mock', '2025-01-01')"
        )
        conn.commit()
        row = conn.execute("SELECT last_insert_rowid() as id").fetchone()
        sid = row["id"]

        # Add some attempts
        conn.execute(
            "INSERT INTO attempts (question_id, session_id, is_correct) VALUES ('q1', ?, 1)",
            (sid,),
        )
        conn.execute(
            "INSERT INTO attempts (question_id, session_id, is_correct) VALUES ('q2', ?, 0)",
            (sid,),
        )
        conn.commit()

        console = Console(file=StringIO(), force_terminal=True, width=80)
        qs = QuizSession(db=seeded_db, session_type="mock", question_count=2, console=console)
        qs.session = type("obj", (object,), {
            "session_id": sid, "session_type": "mock",
            "started_at": "2025-01-01", "tier": None,
        })()

        result = qs.finish()
        assert result is not None
        assert result.correct_count == 1
        assert result.question_count == 2


class TestLoadQuestions:
    """_load_questions function tests."""

    def test_loads_random_no_filter(self, seeded_db):
        """Default loading returns shuffled questions."""
        questions = _load_questions(seeded_db, "mock", None, 5)
        assert len(questions) <= 5
        assert all(not q.is_holdout for q in questions)

    def test_tier_filter(self, seeded_db):
        """Tier filter works."""
        questions = _load_questions(seeded_db, "mock", "tier2", 10)
        assert all(q.tier == "tier2" for q in questions)

    def test_section_gkga(self, seeded_db):
        """gkga_memory session type filters to GK/GA."""
        questions = _load_questions(seeded_db, "gkga_memory", None, 10)
        assert all(q.section == "GK/GA" for q in questions)

    def test_section_english(self, seeded_db):
        """english session type filters to English."""
        questions = _load_questions(seeded_db, "english", None, 10)
        assert all(q.section == "English" for q in questions)

    def test_sm2_review_uses_scheduler(self, seeded_db):
        """sm2_review session type uses scheduler (due questions first)."""
        questions = _load_questions(seeded_db, "sm2_review", None, 10)
        ids = [q.question_id for q in questions]
        # q1 is overdue (2020-01-01), should be included
        assert len(ids) > 0

    def test_excludes_holdout(self, seeded_db):
        """Holdout questions excluded from random loads."""
        questions = _load_questions(seeded_db, "mock", None, 50)
        ids = [q.question_id for q in questions]
        assert "q11" not in ids
