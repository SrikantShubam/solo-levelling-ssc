"""Session and daily reports with Rich-formatted output."""

from __future__ import annotations

from io import StringIO

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .db import Database


def _render_to(
    render_fn,
    console: Console | None = None,
) -> str:
    """Run a render function with a capture console and return the output.

    If an external console is provided, it's only used for side-effect
    rendering (e.g. live terminal display). The return value always comes
    from the internal capture.
    """
    output = StringIO()
    capture = Console(file=output, no_color=True, width=100)
    render_fn(capture)
    rendered = output.getvalue()

    if console is not None:
        console.print(rendered.strip())

    return rendered


def session_report(db: Database, session_id: int, console: Console | None = None) -> str:
    """Generate a Rich-formatted session report.

    Args:
        db: Database instance.
        session_id: The session to report on.
        console: External Console for side-effect display (optional).
                 When None, output is only captured and returned.

    Returns:
        The rendered report as a string.
    """
    def _render(c: Console) -> None:
        conn = db.connect()

        session_row = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()

        if not session_row:
            c.print(f"[red]Session {session_id} not found.[/red]")
            return

        attempts = conn.execute(
            """SELECT a.*, q.section, q.tier
               FROM attempts a
               JOIN questions q ON a.question_id = q.question_id
               WHERE a.session_id = ?
               ORDER BY a.created_at""",
            (session_id,),
        ).fetchall()

        # Header
        c.print(Panel.fit(
            f"[bold]Session #{session_id}[/bold] — {session_row['session_type']}",
            border_style="blue",
        ))
        c.print(f"Started: {session_row['started_at'][:19]}")
        if session_row["ended_at"]:
            c.print(f"Ended:   {session_row['ended_at'][:19]}")
        c.print(f"Tier: {session_row['tier'] or 'N/A'}")
        c.print()

        # Summary stats
        total = len(attempts)
        correct = sum(1 for a in attempts if a["is_correct"])
        skipped = sum(1 for a in attempts if a["student_label"] == "skipped")
        timed_out = sum(1 for a in attempts if a["student_label"] == "timed_out")

        summary = Table(title="Summary", box=None)
        summary.add_column("Metric", style="dim")
        summary.add_column("Value", style="bold")
        summary.add_row("Questions", str(total))
        summary.add_row("Correct", f"[green]{correct}[/green]")
        summary.add_row("Incorrect", f"[red]{total - correct - skipped - timed_out}[/red]")
        summary.add_row("Skipped", str(skipped))
        summary.add_row("Timed Out", str(timed_out))
        if total > 0:
            summary.add_row("Accuracy", f"{correct / total * 100:.1f}%")
        c.print(summary)
        c.print()

        # Per-section breakdown
        if attempts:
            section_table = Table(title="By Section", box=None)
            section_table.add_column("Section")
            section_table.add_column("Total")
            section_table.add_column("Correct")
            section_table.add_column("Accuracy")

            by_section: dict[str, dict[str, int]] = {}
            for a in attempts:
                sec = a["section"]
                if sec not in by_section:
                    by_section[sec] = {"total": 0, "correct": 0}
                by_section[sec]["total"] += 1
                if a["is_correct"]:
                    by_section[sec]["correct"] += 1

            for sec, stats in sorted(by_section.items()):
                pct = stats["correct"] / stats["total"] * 100 if stats["total"] else 0
                color = "green" if pct >= 70 else "yellow" if pct >= 50 else "red"
                section_table.add_row(
                    sec, str(stats["total"]), str(stats["correct"]),
                    f"[{color}]{pct:.0f}%[/{color}]",
                )

            c.print(section_table)
            c.print()

        # Timing breakdown
        if attempts:
            times = [a["time_spent_seconds"] for a in attempts if a["time_spent_seconds"] > 0]
            if times:
                avg_time = sum(times) / len(times)
                c.print(f"Avg time/question: [bold]{avg_time:.0f}s[/bold]")
                c.print(f"Total time: [bold]{sum(times)//60}m {sum(times)%60}s[/bold]")
                c.print()

    return _render_to(_render, console)


def daily_report(db: Database, console: Console | None = None) -> str:
    """Report on today's practice sessions.

    Returns the rendered report as a string.
    """
    def _render(c: Console) -> None:
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).date().isoformat()

        conn = db.connect()

        sessions = conn.execute(
            """SELECT * FROM sessions
               WHERE date(started_at) = ?
               ORDER BY started_at""",
            (today,),
        ).fetchall()

        if not sessions:
            c.print("[dim]No practice sessions recorded today.[/dim]")
            return

        c.print(f"[bold]Today's Practice — {today}[/bold]")
        c.print()

        total_q = 0
        total_c = 0
        total_min = 0

        for s in sessions:
            total_q += s["question_count"] or 0
            total_c += s["correct_count"] or 0
            total_min += s["duration_minutes"] or 0
            status = "[green]✓[/green]" if s["ended_at"] else "[yellow]…[/yellow]"
            c.print(
                f"  {status} {s['session_type']:20s}  "
                f"{s['question_count']:3d} q  "
                f"{s['correct_count']:3d} correct"
            )

        c.print()
        if total_q > 0:
            c.print(f"  Total: {total_q} questions, {total_c} correct "
                    f"({total_c/total_q*100:.0f}% accuracy)")
        if total_min > 0:
            c.print(f"  Time: {total_min} min")

    return _render_to(_render, console)
