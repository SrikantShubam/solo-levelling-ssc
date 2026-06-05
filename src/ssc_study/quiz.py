"""Interactive quiz session engine.

Presents questions, captures answers with timer, scores responses,
and logs attempts + SM-2 state to the database.

Separated from CLI: all Rich Console references are injected, so unit tests
can use `Console(file=io.StringIO())` without needing Click.
"""

from __future__ import annotations

import json
import sqlite3
import time
from datetime import datetime, timezone
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .db import Database
from .models import Attempt, Question, Session, SM2State
from .scheduler import get_due_questions
from .sm2 import compute_sm2, quality_from_performance
from .timer import format_timer, timed_input


class QuizSession:
    """State machine for an interactive quiz session.

    States: PENDING → ACTIVE → COMPLETED | ABANDONED
    """

    def __init__(
        self,
        db: Database,
        session_type: str = "mock",
        tier: str | None = None,
        question_count: int = 25,
        timeout_per_question: int = 120,
        console: Console | None = None,
    ) -> None:
        self.db = db
        self.session_type = session_type
        self.tier = tier
        self.question_count = question_count
        self.timeout_per_question = timeout_per_question
        self.console = console or Console()

        self.session: Session | None = None
        self.questions: list[Question] = []
        self.current_index: int = 0
        self._aborted: bool = False

    # ------------------------------------------------------------------
    # State machine
    # ------------------------------------------------------------------

    def start(self) -> Session:
        """Begin the session: load questions and persist session row."""
        self.questions = _load_questions(
            self.db, self.session_type, self.tier, self.question_count
        )

        conn = self.db.connect()
        cursor = conn.execute(
            """INSERT INTO sessions (session_type, started_at, tier, question_count)
               VALUES (?, ?, ?, ?)""",
            (
                self.session_type,
                datetime.now(timezone.utc).isoformat(),
                self.tier,
                len(self.questions),
            ),
        )
        conn.commit()
        session_id = cursor.lastrowid

        self.session = Session(
            session_type=self.session_type,
            started_at=datetime.now(timezone.utc).isoformat(),
            question_count=len(self.questions),
            tier=self.tier,
            session_id=session_id,
        )
        return self.session

    def has_next(self) -> bool:
        return not self._aborted and self.current_index < len(self.questions)

    def present_next(self) -> Attempt | None:
        """Present one question and return the resulting Attempt (or None if aborted)."""
        if not self.has_next():
            return None

        question = self.questions[self.current_index]
        self.current_index += 1

        attempt = _present_question(
            question=question,
            session_id=self.session.session_id,  # type: ignore[union-attr,arg-type]
            question_number=self.current_index,
            total_questions=len(self.questions),
            timeout_seconds=self.timeout_per_question,
            console=self.console,
        )

        _save_attempt(self.db, attempt, question)
        return attempt

    def run_all(self) -> list[Attempt]:
        """Run the full quiz session and return all attempts."""
        self.start()
        attempts: list[Attempt] = []
        while self.has_next():
            attempt = self.present_next()
            if attempt is None:
                break
            attempts.append(attempt)

        self.finish()
        return attempts

    def abort(self) -> None:
        """Abandon the session (e.g. Ctrl+C)."""
        self._aborted = True
        if self.session and self.session.session_id:
            conn = self.db.connect()
            conn.execute(
                "UPDATE sessions SET ended_at = ?, notes = ? WHERE session_id = ?",
                (datetime.now(timezone.utc).isoformat(), "ABANDONED", self.session.session_id),
            )
            conn.commit()

    def finish(self) -> Session | None:
        """Complete the session and update summary stats."""
        if not self.session or not self.session.session_id:
            return None

        conn = self.db.connect()
        row = conn.execute(
            """SELECT COUNT(*) as total,
                      SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
               FROM attempts WHERE session_id = ?""",
            (self.session.session_id,),
        ).fetchone()

        total = row["total"]
        correct = row["correct"] or 0
        ended_at = datetime.now(timezone.utc).isoformat()

        conn.execute(
            """UPDATE sessions
               SET ended_at = ?, question_count = ?, correct_count = ?
               WHERE session_id = ?""",
            (ended_at, total, correct, self.session.session_id),
        )
        conn.commit()

        return Session(
            session_type=self.session.session_type,
            started_at=self.session.started_at,
            ended_at=ended_at,
            question_count=total,
            correct_count=correct,
            tier=self.session.tier,
            session_id=self.session.session_id,
        )


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------


def _load_questions(
    db: Database,
    session_type: str,
    tier: str | None,
    count: int,
) -> list[Question]:
    """Load questions from the database based on session type.

    Session types:
      - sm2_review: uses SM-2 scheduler (due questions first, then new).
      - gkga_memory / english: section-filtered random.
      - boss_fight / tier2_module / mock / analysis: unfiltered random.
    """
    # SM-2 review sessions use the scheduler
    if session_type == "sm2_review":
        section = None
        return get_due_questions(db, count=count, tier=tier, exclude_holdout=True)

    conn = db.connect()

    query = "SELECT * FROM questions WHERE is_holdout = 0"
    params: list[Any] = []

    if tier:
        query += " AND tier = ?"
        params.append(tier)

    if session_type == "gkga_memory":
        query += " AND section = 'GK/GA'"
    elif session_type == "english":
        query += " AND section = 'English'"

    query += " ORDER BY RANDOM() LIMIT ?"
    params.append(count)

    rows = conn.execute(query, tuple(params)).fetchall()
    return [_row_to_question(r) for r in rows]


def _row_to_question(row: sqlite3.Row) -> Question:
    """Convert a SQLite row to a Question."""
    options_data = json.loads(row["options_json"])
    from .models import Option
    options = [Option(label=o["label"], text=o["text"]) for o in options_data]

    return Question(
        question_id=row["question_id"],
        pdf_name=row["pdf_name"],
        source_page=row["source_page"],
        global_question_number=row["global_question_number"],
        section=row["section"],
        year=row["year"],
        tier=row["tier"],
        question_text=row["question_text"],
        options=options,
        correct_option_label=row["correct_option_label"],
        correct_option_text=row["correct_option_text"],
        chosen_option_label=row["chosen_option_label"],
        question_modality=row["question_modality"],
        visual_required=bool(row["visual_required"]),
        table_required=bool(row["table_required"]),
        math_required=bool(row["math_required"]),
        evidence_status=row["evidence_status"],
        is_holdout=bool(row["is_holdout"]),
        archetype_id=row["archetype_id"],
    )


def _present_question(
    question: Question,
    session_id: int,
    question_number: int,
    total_questions: int,
    timeout_seconds: int,
    console: Console,
) -> Attempt:
    """Display a single question and capture the answer."""
    # Build header
    header = Text.assemble(
        (f"Q{question_number}/{total_questions}  ", "bold cyan"),
        (f"[{question.section}]  ", "dim"),
        (f"Tier: {question.tier}  ", "dim"),
        (f"Modality: {question.question_modality}", "dim"),
    )

    # Build options table
    option_table = Table(show_header=False, box=None, padding=(0, 1))
    option_table.add_column("key", style="bold yellow", width=4)
    option_table.add_column("text")

    for opt in question.options:
        option_table.add_row(f"({opt.label})", opt.text)

    # Question panel
    body = Text(question.question_text, style="white")
    body.append("\n\n")
    # Rich doesn't support adding Table to Text, so use separate prints

    console.print(Panel(header, border_style="blue"))
    console.print(body)
    console.print(option_table)
    console.print()

    # Prompt with timer
    prompt = (
        f"  [bold]Select (1-4)[/bold] "
        f"[dim](s=skip, q=quit, {timeout_seconds}s timeout)[/dim]: "
    )

    start = time.monotonic()
    key, _ = timed_input(
        str(prompt),  # Rich markup won't render in plain input — strip is handled
        timeout_seconds,
        valid_keys={"1", "2", "3", "4", "s", "q"},
    )
    elapsed = time.monotonic() - start
    time_spent = int(elapsed)

    # Determine answer
    user_answer: str | None = None
    is_correct = False
    student_label = "skipped"

    if key == "q":
        console.print("[yellow]Session aborted.[/yellow]")
        raise _QuizAbortError()

    if key == "s" or key is None:
        student_label = "skipped" if key == "s" else "timed_out"
        console.print(
            f"  [dim]{'Skipped' if key == 's' else 'Timed out'} — "
            f"answer was [bold green]({question.correct_option_label})[/bold green][/dim]"
        )
    else:
        user_answer = key
        is_correct = key == question.correct_option_label
        student_label = "correct" if is_correct else "incorrect"

        if is_correct:
            console.print(f"  [bold green]✓ Correct![/bold green] ({format_timer(time_spent)})")
        else:
            console.print(
                f"  [bold red]✗ Incorrect[/bold red] — "
                f"you chose ({key}), answer was "
                f"[bold green]({question.correct_option_label})[/bold green] "
                f"({format_timer(time_spent)})"
            )

    console.print()

    return Attempt(
        question_id=question.question_id,
        session_id=session_id,
        user_answer=user_answer,
        is_correct=is_correct,
        time_spent_seconds=time_spent,
        student_label=student_label,
        quality_score=None,  # computed in _save_attempt
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def _save_attempt(db: Database, attempt: Attempt, question: Question) -> None:
    """Persist an attempt and update SM-2 state."""
    # Compute SM-2 quality
    quality = quality_from_performance(
        is_correct=attempt.is_correct,
        time_spent_seconds=attempt.time_spent_seconds,
    )
    attempt.quality_score = quality

    # Compute timing inference
    t = attempt.time_spent_seconds
    if t < 15:
        timing = "quick"
    elif t <= 60:
        timing = "normal"
    elif t <= 120:
        timing = "slow"
    else:
        timing = "very_slow"

    result = "correct" if attempt.is_correct else "wrong"
    attempt.timing_inference = f"{timing}_{result}"

    # Insert attempt
    conn = db.connect()
    conn.execute(
        """INSERT INTO attempts
           (question_id, session_id, user_answer, is_correct, time_spent_seconds,
            student_label, timing_inference, quality_score)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            attempt.question_id,
            attempt.session_id,
            attempt.user_answer,
            int(attempt.is_correct),
            attempt.time_spent_seconds,
            attempt.student_label,
            attempt.timing_inference,
            quality,
        ),
    )
    conn.commit()

    # Update SM-2 state
    row = conn.execute(
        "SELECT * FROM sm2_state WHERE entity_type = 'question' AND entity_id = ?",
        (question.question_id,),
    ).fetchone()

    prev = SM2State()
    if row:
        prev = SM2State(
            easiness=row["easiness"],
            interval_days=row["interval_days"],
            repetitions=row["repetitions"],
            next_review=row["next_review"],
            last_review=row["last_review"],
            last_quality=row["last_quality"],
        )

    today = datetime.now(timezone.utc).date().isoformat()
    result_state = compute_sm2(quality, prev, today)

    conn.execute(
        """INSERT OR REPLACE INTO sm2_state
           (entity_type, entity_id, easiness, interval_days, repetitions,
            next_review, last_review, last_quality)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "question",
            question.question_id,
            result_state.easiness,
            result_state.interval_days,
            result_state.repetitions,
            result_state.next_review,
            today,
            quality,
        ),
    )
    conn.commit()


class _QuizAbortError(Exception):
    """Internal signal to abort the quiz session."""
