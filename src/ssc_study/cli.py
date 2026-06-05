"""CLI entry point for the SSC study application.

Uses rich-click for structured subcommands with rich formatting.
All business logic is in separate modules — this file only handles
argument parsing and I/O routing.
"""

from __future__ import annotations

from pathlib import Path

import click
import rich_click as _rich_click  # noqa: F401 — registers rich formatter
from rich.console import Console

from . import __version__
from .config import load_config, save_config
from .db import Database
from .loader import import_corpus, verify_import
from .quiz import FoundationPulseError, QuizSession, _QuizAbortError
from .reports import daily_report, session_report

console = Console()


@click.group()
@click.version_option(__version__, prog_name="ssc-study")
def cli() -> None:
    """SSC CGL Scoring Machine — AI-powered study application.

    Practice SSC CGL questions with spaced repetition, timed quizzes,
    and detailed performance analytics.
    """


@cli.command()
@click.option(
    "--pipeline-root",
    default="pipeline_output/p2_gemini",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Path to the pipeline output directory.",
)
@click.option(
    "--db-path",
    default="~/.ssc_study/study.db",
    type=click.Path(path_type=Path),
    help="Path to the SQLite database file.",
)
def import_cmd(pipeline_root: Path, db_path: Path) -> None:
    """Import the SSC corpus into the study database.

    Reads all merged_questions_global_order.json files from the pipeline
    output and loads them into SQLite. Safe to run multiple times —
    skips if the import hash matches a previous run.
    """
    db = Database(db_path)
    console.print(f"[bold]Importing corpus from {pipeline_root}[/bold]")
    console.print(f"Database: {db.path}")

    result = import_corpus(pipeline_root, db_path)

    if result.errors and "Already imported" in result.errors[0]:
        console.print(f"[yellow]{result.errors[0]}[/yellow]")
        return

    console.print(f"[green]Imported {result.question_count} questions "
                  f"from {result.pdf_count} PDFs[/green]")
    console.print(f"  Holdout (sealed): {result.holdout_count}")
    if result.skipped_count:
        console.print(f"  Skipped (invalid): {result.skipped_count}")
    if result.errors:
        for err in result.errors[:10]:
            console.print(f"  [yellow]⚠ {err}[/yellow]")


@cli.command()
@click.option(
    "--db-path",
    default="~/.ssc_study/study.db",
    type=click.Path(path_type=Path),
    help="Path to the SQLite database file.",
)
def verify_cmd(db_path: Path) -> None:
    """Verify the integrity of the imported corpus."""
    result = verify_import(db_path)

    if result["question_count"] == 0:
        console.print("[red]No questions found. Run 'ssc-study import' first.[/red]")
        return

    console.print(f"[bold]Questions:[/bold] {result['question_count']}")
    console.print(f"[bold]Holdout:[/bold]   {result['holdout_count']}")
    console.print()
    console.print("[bold]By Section:[/bold]")
    for section, count in sorted(result["section_counts"].items()):
        console.print(f"  {section}: {count}")
    console.print()
    console.print("[bold]By Tier:[/bold]")
    for tier, count in sorted(result["tier_counts"].items()):
        console.print(f"  {tier}: {count}")

    if result["has_errors"]:
        console.print()
        for err in result["error_details"]:
            console.print(f"[red]✗ {err}[/red]")
        raise SystemExit(1)
    else:
        console.print()
        console.print("[green]✓ All integrity checks passed.[/green]")


@cli.command()
@click.option(
    "--session-type",
    type=click.Choice([
        "sm2_review", "boss_fight", "tier2_module", "gkga_memory",
        "english", "mock", "analysis", "remediation",
        "foundation_pulse",
    ]),
    default="mock",
    help="Type of practice session.",
)
@click.option("--count", default=25, help="Number of questions.", show_default=True)
@click.option("--tier", type=click.Choice(["tier1", "tier2"]), help="Tier filter.")
@click.option(
    "--timeout", default=120, help="Seconds per question.", show_default=True
)
@click.option(
    "--db-path",
    default="~/.ssc_study/study.db",
    type=click.Path(path_type=Path),
    help="Path to the SQLite database.",
)
def quiz(session_type: str, count: int, tier: str | None, timeout: int, db_path: Path) -> None:
    """Start an interactive quiz session.

    Answer questions against a timer. Your responses are logged and
    feed into the SM-2 spaced repetition scheduler.
    """
    db = Database(db_path)

    # Check that corpus is imported
    conn = db.connect()
    q_count = conn.execute("SELECT COUNT(*) as c FROM questions").fetchone()["c"]
    if q_count == 0:
        console.print("[red]No questions in database. Run 'ssc-study import' first.[/red]")
        raise SystemExit(1)

    console.print(
        f"[bold]Starting {session_type} session[/bold] — "
        f"{count} questions, {timeout}s per question"
    )

    if tier:
        console.print(f"  Tier filter: {tier}")
    console.print()

    quiz_session = QuizSession(
        db=db,
        session_type=session_type,
        tier=tier,
        question_count=count,
        timeout_per_question=timeout,
        console=console,
    )

    try:
        quiz_session.start()
        console.print(f"Loaded {len(quiz_session.questions)} questions\n")

        while quiz_session.has_next():
            quiz_session.present_next()

        finished = quiz_session.finish()
        if finished:
            console.print()
            console.print(f"[bold green]Session complete![/bold green] "
                          f"{finished.correct_count}/{finished.question_count} correct")
            console.print(f"Run [bold]ssc-study report --session {finished.session_id}[/bold] "
                          f"for details.")
    except FoundationPulseError as e:
        console.print(f"[red]{e}[/red]")
        console.print("[yellow]Foundation pulse aborted — no session created.[/yellow]")
        return
    except _QuizAbortError:
        quiz_session.abort()
        console.print("[yellow]Session abandoned.[/yellow]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Session interrupted (Ctrl+C). Saving partial state...[/yellow]")
        quiz_session.abort()


@cli.command()
@click.option("--session", "session_id", type=int, help="Show report for a specific session.")
@click.option("--daily", is_flag=True, help="Show today's practice summary.")
@click.option(
    "--db-path",
    default="~/.ssc_study/study.db",
    type=click.Path(path_type=Path),
    help="Path to the SQLite database.",
)
def report(session_id: int | None, daily: bool, db_path: Path) -> None:
    """Show practice session reports."""
    db = Database(db_path)

    if session_id:
        session_report(db, session_id, console)
    elif daily:
        daily_report(db, console)
    else:
        daily_report(db, console)


@cli.command()
@click.option("--db-path", type=click.Path(path_type=Path), help="Set database path.")
@click.option("--show", "show_config", is_flag=True, help="Display current configuration.")
def config(db_path: Path | None, show_config: bool) -> None:
    """View or update user configuration."""
    cfg = load_config()

    if show_config:
        console.print("[bold]Current Configuration:[/bold]")
        console.print(f"  DB path:            {cfg.db_path}")
        console.print(f"  Tier-1 floor:       {cfg.tier1_floor_target}")
        console.print(f"  Tier-2 floor:       {cfg.tier2_floor_target}")
        console.print(f"  Archetype probe:    {cfg.archetype_probe_count} q")
        console.print(f"  Unlock threshold:   {cfg.archetype_unlock_accuracy:.0%}")
        console.print(f"  Holdout ratio:      {cfg.holdout_ratio:.0%}")
        console.print(f"  Backup reminder:    {cfg.backup_reminder}")
        console.print()
        console.print("[bold]Daily Split (minutes):[/bold]")
        for activity, mins in cfg.daily_split_minutes.items():
            console.print(f"  {activity}: {mins}")
        return

    if db_path:
        cfg.db_path = str(db_path)
        save_config(cfg)
        console.print(f"[green]Database path set to {db_path}[/green]")


@cli.command()
@click.option(
    "--db-path",
    default="~/.ssc_study/study.db",
    type=click.Path(path_type=Path),
    help="Path to the SQLite database.",
)
def readiness(db_path: Path) -> None:
    """Show exam readiness dashboard."""
    from .readiness import compute_readiness

    db = Database(db_path)
    report = compute_readiness(db)

    if report.ready:
        console.print("[bold green]✓ READY[/bold green] — All conditions met!")
    else:
        console.print(f"[bold yellow]NOT READY[/bold yellow] — {len(report.missing)} condition(s) not met")
        console.print()

    for name, check in report.checks.items():
        icon = "[green]✓[/green]" if check.passed else "[red]✗[/red]"
        console.print(f"  {icon} {check.name}: {check.actual}")
        if not check.passed and check.reason:
            console.print(f"       [dim]{check.reason}[/dim]")

    console.print()
    passed = len(report.checks) - len(report.missing)
    total = len(report.checks)
    console.print(f"[bold]{passed}/{total}[/bold] checks passing ({passed/total*100:.0f}%)")


@cli.group()
def audit() -> None:
    """Manage exam notification audits."""


@audit.command("trigger")
@click.option("--notification-date", help="Notification date (YYYY-MM-DD).")
@click.option("--change", "changes", multiple=True, help="Detected changes.")
@click.option(
    "--db-path",
    default="~/.ssc_study/study.db",
    type=click.Path(path_type=Path),
    help="Path to the SQLite database.",
)
def audit_trigger(notification_date: str | None, changes: tuple[str, ...], db_path: Path) -> None:
    """Trigger a notification audit (when exam notification drops)."""
    from .audit import trigger_notification_audit

    db = Database(db_path)
    notif_data = {}
    if notification_date:
        notif_data["notification_date"] = notification_date
    if changes:
        notif_data["changes"] = list(changes)

    result = trigger_notification_audit(db, notif_data)
    console.print(f"[bold]Audit #{result['audit_id']}[/bold] — {result['message']}")
    if result["paused"]:
        console.print("[yellow]Advancement paused. Run 'ssc-study audit complete' after review.[/yellow]")


@audit.command("complete")
@click.option("--audit-id", type=int, required=True, help="Audit ID to complete.")
@click.option(
    "--db-path",
    default="~/.ssc_study/study.db",
    type=click.Path(path_type=Path),
    help="Path to the SQLite database.",
)
def audit_complete(audit_id: int, db_path: Path) -> None:
    """Complete a notification audit with review."""
    from .audit import NotificationChange, complete_audit

    db = Database(db_path)
    # For CLI, mark as minor with a basic note
    result = complete_audit(db, audit_id, [
        NotificationChange("other", "Manual review completed", "minor"),
    ])
    console.print(result["message"])
    if result["affected_queues"]:
        console.print(f"  Affected queues: {', '.join(result['affected_queues'])}")


@audit.command("status")
@click.option(
    "--db-path",
    default="~/.ssc_study/study.db",
    type=click.Path(path_type=Path),
    help="Path to the SQLite database.",
)
def audit_status(db_path: Path) -> None:
    """Check if advancement is paused by an active audit."""
    from .audit import get_audit_history, is_audit_paused

    db = Database(db_path)
    status = is_audit_paused(db)

    if status["paused"]:
        console.print("[yellow]ADVANCEMENT PAUSED[/yellow]")
        console.print(f"  Reason: {status['reason']}")
    else:
        console.print("[green]No active advancement pause.[/green]")

    history = get_audit_history(db, limit=5)
    if history:
        console.print()
        console.print("[bold]Recent audits:[/bold]")
        for h in history:
            console.print(f"  #{h['audit_id']} ({h['notification_date'] or 'N/A'}): {h['changes_detected'][:60] or 'pending'}")


def main(argv: list[str] | None = None) -> int:
    """Entry point for console_scripts."""
    try:
        cli.main(args=argv, standalone_mode=False)
        return 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as exc:
        console.print(f"[red]Error: {exc}[/red]")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
