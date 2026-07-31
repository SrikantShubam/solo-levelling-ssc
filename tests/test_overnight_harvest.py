from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def load_runner():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "run_overnight_harvest.py"
    spec = importlib.util.spec_from_file_location("run_overnight_harvest", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_pdf(path: Path) -> None:
    path.write_bytes(b"%PDF-1.4\n% test\n")


def test_batch_skips_completed_outputs_and_updates_manifest(tmp_path: Path) -> None:
    runner = load_runner()
    pdf_dir = tmp_path / "pdfs"
    out_root = tmp_path / "out"
    pdf_dir.mkdir()
    write_pdf(pdf_dir / "done.pdf")
    write_pdf(pdf_dir / "todo.pdf")

    done_out = out_root / "done"
    done_out.mkdir(parents=True)
    (done_out / "merged_questions_global_order.json").write_text(
        json.dumps({"questions": [{"global_question_number": 1}]}),
        encoding="utf-8",
    )

    calls: list[str] = []

    def fake_extract(pdf_path: Path, output_dir: Path) -> runner.PdfRunResult:
        calls.append(pdf_path.name)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "merged_questions_global_order.json").write_text(
            json.dumps({"questions": [{"global_question_number": 1}, {"global_question_number": 2}]}),
            encoding="utf-8",
        )
        return runner.inspect_pdf_output(pdf_path, output_dir)

    result = runner.run_batch(
        pdf_dir=pdf_dir,
        output_root=out_root,
        concurrency=2,
        extractor=fake_extract,
        api_key_and_spec=("test-key", type("Spec", (), {"provider": "openrouter", "endpoint": "test"})()),
        usage_fetcher=lambda _key: {"usage": 1.0},
    )

    assert calls == ["todo.pdf"]
    assert result["statuses"]["done"] == 2
    status = json.loads((out_root / "batch_status.json").read_text(encoding="utf-8"))
    assert status["pdfs"]["done.pdf"]["status"] == "done"
    assert status["pdfs"]["done.pdf"]["skipped"] is True
    assert status["pdfs"]["todo.pdf"]["status"] == "done"
    assert status["pdfs"]["todo.pdf"]["question_count"] == 2


def test_batch_recovers_stale_in_progress_entries(tmp_path: Path) -> None:
    runner = load_runner()
    pdf_dir = tmp_path / "pdfs"
    out_root = tmp_path / "out"
    pdf_dir.mkdir()
    out_root.mkdir()
    write_pdf(pdf_dir / "resume.pdf")
    (out_root / "batch_status.json").write_text(
        json.dumps(
            {
                "pdfs": {
                    "resume.pdf": {
                        "pdf": str(pdf_dir / "resume.pdf"),
                        "status": "in_progress",
                        "reason": "previous run died",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    def fake_extract(pdf_path: Path, output_dir: Path) -> runner.PdfRunResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "merged_questions_global_order.json").write_text(
            json.dumps({"questions": [{"global_question_number": 1}]}),
            encoding="utf-8",
        )
        return runner.inspect_pdf_output(pdf_path, output_dir)

    runner.run_batch(
        pdf_dir=pdf_dir,
        output_root=out_root,
        concurrency=1,
        extractor=fake_extract,
        api_key_and_spec=("test-key", type("Spec", (), {"provider": "openrouter", "endpoint": "test"})()),
        usage_fetcher=lambda _key: {"usage": 1.0},
    )

    status = json.loads((out_root / "batch_status.json").read_text(encoding="utf-8"))
    assert status["pdfs"]["resume.pdf"]["status"] == "done"
    assert status["pdfs"]["resume.pdf"]["reason"] is None


def test_batch_budget_stop_marks_unlaunched_pdfs(tmp_path: Path) -> None:
    runner = load_runner()
    pdf_dir = tmp_path / "pdfs"
    out_root = tmp_path / "out"
    pdf_dir.mkdir()
    for name in ["a.pdf", "b.pdf", "c.pdf"]:
        write_pdf(pdf_dir / name)

    calls: list[str] = []

    def fake_extract(pdf_path: Path, output_dir: Path) -> runner.PdfRunResult:
        calls.append(pdf_path.name)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "merged_questions_global_order.json").write_text(
            json.dumps({"questions": [{"global_question_number": 1}], "page_counts": [{"page": 1, "page_status": "OK"}]}),
            encoding="utf-8",
        )
        return runner.inspect_pdf_output(pdf_path, output_dir)

    usages = iter([10.0, 15.0, 15.0])
    runner.run_batch(
        pdf_dir=pdf_dir,
        output_root=out_root,
        concurrency=1,
        extractor=fake_extract,
        budget_limit_usd=4.90,
        api_key_and_spec=("test-key", type("Spec", (), {"provider": "openrouter", "endpoint": "test"})()),
        usage_fetcher=lambda _key: {"usage": next(usages)},
    )

    status = json.loads((out_root / "batch_status.json").read_text(encoding="utf-8"))
    assert calls == ["a.pdf"]
    assert status["budget_stop"]["status"] == "triggered"
    assert status["pdfs"]["b.pdf"]["status"] == "stopped"
    assert status["pdfs"]["c.pdf"]["status"] == "stopped"
