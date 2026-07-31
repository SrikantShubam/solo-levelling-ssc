from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, NamedTuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ssc_corpus.cli import _first_env_value, _load_env_or_raise, _primary_model_spec
from ssc_corpus.extraction import (
    ExtractionResult,
    _call_openai_compatible_vision_page,
    _finalize_extraction_result,
    _read_cached_page_json,
    extract_pdf_with_openai_compatible_vision,
    render_pdf_pages,
)


DEFAULT_PDF_DIR = Path("data/harvest_pdfs")
DEFAULT_OUTPUT_ROOT = Path("pipeline_output/harvest_batch")
DEFAULT_ENV_FILE = Path(".env")
DEFAULT_MODEL = "qwen/qwen3-vl-32b-instruct"
DEFAULT_PROVIDER = "openrouter"
DEFAULT_PAGE_DELAY_SECONDS = 0.25
DEFAULT_BUDGET_LIMIT_USD = 4.90
DEFAULT_LARGE_PDF_PAGE_WORKERS = 4
DEFAULT_LARGE_PDF_PAGE_THRESHOLD = 200
OPENROUTER_KEY_URL = "https://openrouter.ai/api/v1/key"
REMOTE_COMPILATION_GLOB = "manstein@192.168.1.14:~/ssc-pdf-harvest/*testbook_compilation*.pdf"


class PdfRunResult(NamedTuple):
    pdf_name: str
    output_dir: str
    status: str
    question_count: int | None
    page_count: int | None
    page_success_count: int
    page_fail_count: int
    qc_status: str | None
    reason: str | None
    skipped: bool
    elapsed_seconds: float | None = None


Extractor = Callable[[Path, Path], PdfRunResult]


def now_ts() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def read_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"created_at": now_ts(), "pdfs": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"created_at": now_ts(), "pdfs": {}}
    if not isinstance(data, dict):
        data = {}
    data.setdefault("created_at", now_ts())
    data.setdefault("pdfs", {})
    if not isinstance(data["pdfs"], dict):
        data["pdfs"] = {}
    return data


def enumerate_pdfs(pdf_dir: Path) -> list[Path]:
    return sorted(pdf_dir.glob("*.pdf"), key=lambda path: path.name.lower())


def output_dir_for(output_root: Path, pdf_path: Path) -> Path:
    return output_root / pdf_path.stem


def merged_path_for(output_dir: Path) -> Path:
    return output_dir / "merged_questions_global_order.json"


def count_pdf_pages(pdf_path: Path) -> int | None:
    try:
        import fitz
    except ImportError:
        return None
    try:
        doc = fitz.open(str(pdf_path))
        try:
            return int(doc.page_count)
        finally:
            doc.close()
    except Exception:
        return None


def _read_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def inspect_pdf_output(pdf_path: Path, output_dir: Path, *, skipped: bool = False) -> PdfRunResult:
    merged = _read_json(merged_path_for(output_dir))
    page_count = count_pdf_pages(pdf_path)
    question_count: int | None = None
    page_success_count = 0
    page_fail_count = 0
    qc_status = None
    reason = None
    status = "failed"

    if isinstance(merged, dict):
        questions = merged.get("questions")
        page_counts = merged.get("page_counts")
        if isinstance(questions, list):
            question_count = len(questions)
        if isinstance(page_counts, list):
            for row in page_counts:
                if not isinstance(row, dict):
                    continue
                if row.get("page_status") == "OK":
                    page_success_count += 1
                else:
                    page_fail_count += 1
        qc_status = merged.get("structural_status") or merged.get("qc_status")
        status = "done" if question_count is not None else "failed"
        if status == "failed":
            reason = "missing_questions_array"
    else:
        reason = "missing_or_invalid_merged_questions_global_order_json"

    if page_count is None:
        page_json_dir = output_dir / "page_json"
        observed_pages = list(page_json_dir.glob("page_*.json")) if page_json_dir.exists() else []
        page_count = len(observed_pages) or None
    if isinstance(merged, dict) and not page_success_count and not page_fail_count:
        raw_pages = merged.get("page_count")
        if isinstance(raw_pages, int):
            page_success_count = raw_pages if status == "done" else 0

    return PdfRunResult(
        pdf_name=pdf_path.name,
        output_dir=str(output_dir),
        status=status,
        question_count=question_count,
        page_count=page_count,
        page_success_count=page_success_count,
        page_fail_count=page_fail_count,
        qc_status=str(qc_status) if qc_status else None,
        reason=reason,
        skipped=skipped,
    )


def in_progress_counts(output_dir: Path) -> tuple[int, int]:
    page_json_dir = output_dir / "page_json"
    if not page_json_dir.exists():
        return 0, 0
    ok = 0
    failed = 0
    for path in page_json_dir.glob("page_*.json"):
        data = _read_json(path)
        if isinstance(data, dict) and data.get("page_status") == "ERROR":
            failed += 1
        else:
            ok += 1
    return ok, failed


def query_openrouter_usage(api_key: str) -> dict[str, Any]:
    request = Request(OPENROUTER_KEY_URL, headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"OpenRouter key query failed: HTTP {exc.code}: {body}") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"OpenRouter key query failed: {type(exc).__name__}: {exc}") from exc
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        raise RuntimeError("OpenRouter key query returned no data object")
    usage = data.get("usage")
    if usage is None:
        raise RuntimeError("OpenRouter key query returned no usage field")
    data["usage"] = float(usage)
    return data


def load_openrouter_key(env_file: Path, model: str = DEFAULT_MODEL) -> tuple[str, Any]:
    env = _load_env_or_raise(env_file)
    spec = _primary_model_spec(DEFAULT_PROVIDER, model)
    api_key = _first_env_value(env, spec.env_key_names)
    if not api_key:
        raise ValueError("No API key found for provider openrouter")
    return api_key, spec


def result_to_manifest_entry(pdf_path: Path, result: PdfRunResult) -> dict[str, Any]:
    return {
        "pdf": str(pdf_path),
        "output_dir": result.output_dir,
        "status": result.status,
        "question_count": result.question_count,
        "page_count": result.page_count,
        "page_success_count": result.page_success_count,
        "page_fail_count": result.page_fail_count,
        "qc_status": result.qc_status,
        "reason": result.reason,
        "skipped": result.skipped,
        "elapsed_seconds": result.elapsed_seconds,
        "updated_at": now_ts(),
    }


def write_manifest(
    manifest_path: Path,
    manifest: dict[str, Any],
    *,
    start_monotonic: float | None = None,
    all_pdfs: list[Path] | None = None,
) -> None:
    manifest["updated_at"] = now_ts()
    counts: dict[str, int] = {}
    total_pages = 0
    completed_pages = 0
    completed_pdfs = 0
    for pdf_path in all_pdfs or []:
        entry = manifest.get("pdfs", {}).get(pdf_path.name, {})
        page_count = entry.get("page_count")
        if not isinstance(page_count, int):
            page_count = count_pdf_pages(pdf_path) or 0
            if page_count:
                entry["page_count"] = page_count
        total_pages += int(page_count or 0)
        if entry.get("status") == "in_progress":
            ok, failed = in_progress_counts(Path(str(entry.get("output_dir"))))
            entry["page_success_count"] = ok
            entry["page_fail_count"] = failed
        done_pages = int(entry.get("page_success_count") or 0) + int(entry.get("page_fail_count") or 0)
        completed_pages += min(done_pages, int(page_count or done_pages))
        if entry.get("status") in {"done", "failed", "stopped"}:
            completed_pdfs += 1
    for entry in manifest.get("pdfs", {}).values():
        status = str(entry.get("status", "unknown"))
        counts[status] = counts.get(status, 0) + 1
    elapsed = time.monotonic() - start_monotonic if start_monotonic else manifest.get("elapsed_seconds", 0)
    pages_per_second = (completed_pages / elapsed) if elapsed and completed_pages else 0.0
    remaining_pages = max(total_pages - completed_pages, 0)
    projected_remaining = remaining_pages / pages_per_second if pages_per_second else None
    manifest["summary"] = {
        "statuses": counts,
        "pdf_total": len(all_pdfs or manifest.get("pdfs", {})),
        "pdf_terminal": completed_pdfs,
        "page_total": total_pages,
        "page_completed": completed_pages,
        "elapsed_seconds": elapsed,
        "pages_per_second": pages_per_second,
        "projected_remaining_seconds": projected_remaining,
        "projected_total_seconds": elapsed + projected_remaining if projected_remaining is not None else None,
        "target_seconds": 7200,
    }
    atomic_write_json(manifest_path, manifest)


def pull_remote_compilations(pdf_dir: Path) -> dict[str, Any]:
    pdf_dir.mkdir(parents=True, exist_ok=True)
    existing = [path for path in enumerate_pdfs(pdf_dir) if path.name.endswith("_testbook_compilation.pdf")]
    if len(existing) >= 3:
        return {"status": "skipped_present", "existing": [path.name for path in existing]}
    before = {path.name for path in enumerate_pdfs(pdf_dir)}
    command = ["scp", REMOTE_COMPILATION_GLOB, str(pdf_dir)]
    started_at = now_ts()
    try:
        completed = subprocess.run(command, text=True, capture_output=True, timeout=300)
    except FileNotFoundError as exc:
        return {"status": "failed", "command": command, "started_at": started_at, "finished_at": now_ts(), "reason": str(exc)}
    except subprocess.TimeoutExpired:
        return {"status": "failed", "command": command, "started_at": started_at, "finished_at": now_ts(), "reason": "scp timed out after 300s"}
    after = {path.name for path in enumerate_pdfs(pdf_dir)}
    compilations = sorted(path.name for path in enumerate_pdfs(pdf_dir) if path.name.endswith("_testbook_compilation.pdf"))
    return {
        "status": "ok" if completed.returncode == 0 and len(compilations) >= 3 else "failed",
        "command": command,
        "started_at": started_at,
        "finished_at": now_ts(),
        "returncode": completed.returncode,
        "added": sorted(after - before),
        "compilation_pdfs": compilations,
        "stdout": completed.stdout[-2000:],
        "stderr": completed.stderr[-2000:],
    }


def recover_interrupted_entries(manifest: dict[str, Any]) -> None:
    for entry in manifest.get("pdfs", {}).values():
        if entry.get("status") == "in_progress":
            entry["status"] = "pending"
            entry["reason"] = "reset from stale in_progress entry at startup"
            entry["updated_at"] = now_ts()


def extract_one_pdf(
    pdf_path: Path,
    output_dir: Path,
    *,
    env_file: Path = DEFAULT_ENV_FILE,
    model: str = DEFAULT_MODEL,
    page_delay_seconds: float = DEFAULT_PAGE_DELAY_SECONDS,
    large_pdf_page_workers: int = DEFAULT_LARGE_PDF_PAGE_WORKERS,
    large_pdf_page_threshold: int = DEFAULT_LARGE_PDF_PAGE_THRESHOLD,
    force: bool = False,
) -> PdfRunResult:
    started = time.monotonic()
    api_key, spec = load_openrouter_key(env_file, model)
    page_count = count_pdf_pages(pdf_path) or 0
    if page_count >= large_pdf_page_threshold and large_pdf_page_workers > 1:
        extraction_result = extract_pdf_with_openai_compatible_vision_parallel_pages(
            pdf_path=pdf_path.resolve(),
            output_dir=output_dir.resolve(),
            provider=spec.provider,
            model_name=spec.model,
            endpoint=spec.endpoint,
            api_key=api_key,
            expected_questions=100,
            force=force,
            page_workers=large_pdf_page_workers,
        )
    else:
        extraction_result = extract_pdf_with_openai_compatible_vision(
            pdf_path=pdf_path.resolve(),
            output_dir=output_dir.resolve(),
            provider=spec.provider,
            model_name=spec.model,
            endpoint=spec.endpoint,
            api_key=api_key,
            expected_questions=100,
            force=force,
            page_delay_seconds=page_delay_seconds,
        )
    inspected = inspect_pdf_output(pdf_path, output_dir)
    return PdfRunResult(
        pdf_name=inspected.pdf_name,
        output_dir=inspected.output_dir,
        status=inspected.status,
        question_count=inspected.question_count,
        page_count=inspected.page_count,
        page_success_count=inspected.page_success_count,
        page_fail_count=inspected.page_fail_count,
        qc_status=extraction_result.qc_status or inspected.qc_status,
        reason=inspected.reason,
        skipped=False,
        elapsed_seconds=time.monotonic() - started,
    )


def extract_pdf_with_openai_compatible_vision_parallel_pages(
    *,
    pdf_path: Path,
    output_dir: Path,
    provider: str,
    model_name: str,
    endpoint: str,
    api_key: str,
    expected_questions: int | None = 100,
    force: bool = False,
    page_workers: int = DEFAULT_LARGE_PDF_PAGE_WORKERS,
) -> ExtractionResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    image_paths = render_pdf_pages(pdf_path, output_dir / "page_images")
    page_json_dir = output_dir / "page_json"
    page_json_dir.mkdir(parents=True, exist_ok=True)
    page_results: list[dict[str, Any] | None] = [None] * len(image_paths)
    work: list[tuple[int, Path, Path]] = []
    for index, image_path in enumerate(image_paths, start=1):
        json_path = page_json_dir / f"page_{index:02d}.json"
        if json_path.exists() and not force:
            cached = _read_cached_page_json(json_path)
            if cached is not None:
                page_results[index - 1] = cached
                continue
        work.append((index, image_path, json_path))

    def extract_page(item: tuple[int, Path, Path]) -> tuple[int, dict[str, Any]]:
        page_number, image_path, json_path = item
        page_result = _call_openai_compatible_vision_page(
            provider=provider,
            model_name=model_name,
            endpoint=endpoint,
            api_key=api_key,
            image_path=image_path,
            page_number=page_number,
        )
        tmp = json_path.with_suffix(json_path.suffix + ".tmp")
        tmp.write_text(json.dumps(page_result, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(json_path)
        return page_number, page_result

    max_workers = max(1, min(int(page_workers), len(work) or 1))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(extract_page, item) for item in work]
        for future in concurrent.futures.as_completed(futures):
            page_number, page_result = future.result()
            page_results[page_number - 1] = page_result

    ordered = [result for result in page_results if result is not None]
    return _finalize_extraction_result(
        pdf_path=pdf_path,
        output_dir=output_dir,
        page_results=ordered,
        expected_questions=expected_questions,
        extraction_method=f"{provider} {model_name} parallel-page visual PNG extraction, merged in page/visual order",
    )


def extract_one_pdf_worker(args: tuple[str, str, str, str, float, int, int, bool]) -> PdfRunResult:
    pdf_path, output_dir, env_file, model, page_delay_seconds, large_pdf_page_workers, large_pdf_page_threshold, force = args
    return extract_one_pdf(
        Path(pdf_path),
        Path(output_dir),
        env_file=Path(env_file),
        model=model,
        page_delay_seconds=float(page_delay_seconds),
        large_pdf_page_workers=int(large_pdf_page_workers),
        large_pdf_page_threshold=int(large_pdf_page_threshold),
        force=bool(force),
    )


def _pending_from_manifest(pdfs: list[Path], manifest: dict[str, Any], output_root: Path) -> list[Path]:
    pending: list[Path] = []
    for pdf_path in pdfs:
        output_dir = output_dir_for(output_root, pdf_path)
        existing = inspect_pdf_output(pdf_path, output_dir, skipped=True)
        if existing.status == "done":
            manifest["pdfs"][pdf_path.name] = result_to_manifest_entry(pdf_path, existing)
            continue
        previous = manifest["pdfs"].get(pdf_path.name, {})
        manifest["pdfs"][pdf_path.name] = {
            "pdf": str(pdf_path),
            "output_dir": str(output_dir),
            "status": "pending",
            "question_count": previous.get("question_count"),
            "page_count": existing.page_count or previous.get("page_count") or count_pdf_pages(pdf_path),
            "page_success_count": existing.page_success_count,
            "page_fail_count": existing.page_fail_count,
            "reason": previous.get("reason"),
            "updated_at": now_ts(),
        }
        pending.append(pdf_path)
    return pending


def run_batch(
    *,
    pdf_dir: Path = DEFAULT_PDF_DIR,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    concurrency: int = 4,
    env_file: Path = DEFAULT_ENV_FILE,
    extractor: Extractor | None = None,
    limit: int | None = None,
    pull_remote: bool = False,
    model: str = DEFAULT_MODEL,
    page_delay_seconds: float = DEFAULT_PAGE_DELAY_SECONDS,
    budget_limit_usd: float = DEFAULT_BUDGET_LIMIT_USD,
    large_pdf_page_workers: int = DEFAULT_LARGE_PDF_PAGE_WORKERS,
    large_pdf_page_threshold: int = DEFAULT_LARGE_PDF_PAGE_THRESHOLD,
    force: bool = False,
    api_key_and_spec: tuple[str, Any] | None = None,
    usage_fetcher: Callable[[str], dict[str, Any]] = query_openrouter_usage,
) -> dict[str, Any]:
    pdf_dir = pdf_dir.resolve()
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    manifest_path = output_root / "batch_status.json"
    manifest = read_manifest(manifest_path)
    recover_interrupted_entries(manifest)
    api_key, spec = api_key_and_spec or load_openrouter_key(env_file, model)
    start_key_data = usage_fetcher(api_key)
    start_usage = float(start_key_data["usage"])
    manifest.update(
        {
            "pdf_dir": str(pdf_dir),
            "output_root": str(output_root),
            "provider": DEFAULT_PROVIDER,
            "model": model,
            "endpoint": spec.endpoint,
            "concurrency": concurrency,
            "page_delay_seconds": page_delay_seconds,
            "large_pdf_page_workers": large_pdf_page_workers,
            "large_pdf_page_threshold": large_pdf_page_threshold,
            "budget_limit_usd": budget_limit_usd,
            "openrouter_start_usage": start_usage,
            "openrouter_start_key_data": {key: value for key, value in start_key_data.items() if key != "hash"},
        }
    )
    if pull_remote:
        manifest["remote_pull"] = pull_remote_compilations(pdf_dir)
    pdfs = enumerate_pdfs(pdf_dir)
    if limit is not None:
        pdfs = pdfs[:limit]
    pending = _pending_from_manifest(pdfs, manifest, output_root)
    start_monotonic = time.monotonic()
    write_manifest(manifest_path, manifest, start_monotonic=start_monotonic, all_pdfs=pdfs)
    if not pending:
        return dict(manifest.get("summary", {}))

    max_workers = max(1, min(int(concurrency), len(pending)))
    pending_iter = iter(pending)
    futures: dict[concurrent.futures.Future[PdfRunResult], Path] = {}
    stopped_for_budget = False

    def submit_next(executor: concurrent.futures.Executor) -> bool:
        try:
            pdf_path = next(pending_iter)
        except StopIteration:
            return False
        output_dir = output_dir_for(output_root, pdf_path)
        manifest["pdfs"][pdf_path.name].update(
            {"status": "in_progress", "reason": None, "started_at": now_ts(), "updated_at": now_ts()}
        )
        write_manifest(manifest_path, manifest, start_monotonic=start_monotonic, all_pdfs=pdfs)
        if extractor is not None:
            future = executor.submit(extractor, pdf_path, output_dir)
        else:
            future = executor.submit(
                extract_one_pdf_worker,
                (
                    str(pdf_path),
                    str(output_dir),
                    str(env_file.resolve()),
                    model,
                    page_delay_seconds,
                    large_pdf_page_workers,
                    large_pdf_page_threshold,
                    force,
                ),
            )
        futures[future] = pdf_path
        return True

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for _ in range(max_workers):
            if not submit_next(executor):
                break
        while futures:
            done, _ = concurrent.futures.wait(futures, timeout=15, return_when=concurrent.futures.FIRST_COMPLETED)
            if not done:
                write_manifest(manifest_path, manifest, start_monotonic=start_monotonic, all_pdfs=pdfs)
                continue
            for future in done:
                pdf_path = futures.pop(future)
                try:
                    result = future.result()
                except Exception as exc:
                    result = PdfRunResult(
                        pdf_name=pdf_path.name,
                        output_dir=str(output_dir_for(output_root, pdf_path)),
                        status="failed",
                        question_count=None,
                        page_count=count_pdf_pages(pdf_path),
                        page_success_count=0,
                        page_fail_count=0,
                        qc_status=None,
                        reason=f"{type(exc).__name__}: {exc}",
                        skipped=False,
                    )
                manifest["pdfs"][pdf_path.name] = result_to_manifest_entry(pdf_path, result)
                try:
                    current_usage = float(usage_fetcher(api_key)["usage"])
                    manifest["openrouter_current_usage"] = current_usage
                    manifest["openrouter_batch_delta"] = current_usage - start_usage
                    if current_usage - start_usage >= budget_limit_usd:
                        stopped_for_budget = True
                        manifest["budget_stop"] = {
                            "status": "triggered",
                            "usage_delta": current_usage - start_usage,
                            "limit": budget_limit_usd,
                            "triggered_at": now_ts(),
                        }
                except RuntimeError as exc:
                    manifest["openrouter_usage_query_error"] = str(exc)
                write_manifest(manifest_path, manifest, start_monotonic=start_monotonic, all_pdfs=pdfs)
                if not stopped_for_budget:
                    submit_next(executor)
    if stopped_for_budget:
        for pdf_path in pending:
            entry = manifest["pdfs"].get(pdf_path.name, {})
            if entry.get("status") == "pending":
                entry["status"] = "stopped"
                entry["reason"] = "budget stop triggered before launch"
                entry["updated_at"] = now_ts()
    try:
        final_usage = float(usage_fetcher(api_key)["usage"])
        manifest["openrouter_current_usage"] = final_usage
        manifest["openrouter_batch_delta"] = final_usage - start_usage
    except RuntimeError as exc:
        manifest["openrouter_usage_query_error"] = str(exc)
    write_manifest(manifest_path, manifest, start_monotonic=start_monotonic, all_pdfs=pdfs)
    return dict(manifest.get("summary", {}))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SSC OpenRouter harvest extraction batch.")
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_FILE)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--skip-remote-pull", action="store_true")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--page-delay-seconds", type=float, default=DEFAULT_PAGE_DELAY_SECONDS)
    parser.add_argument("--large-pdf-page-workers", type=int, default=DEFAULT_LARGE_PDF_PAGE_WORKERS)
    parser.add_argument("--large-pdf-page-threshold", type=int, default=DEFAULT_LARGE_PDF_PAGE_THRESHOLD)
    parser.add_argument("--budget-limit-usd", type=float, default=DEFAULT_BUDGET_LIMIT_USD)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = run_batch(
            pdf_dir=args.pdf_dir,
            output_root=args.out,
            concurrency=args.concurrency,
            env_file=args.env_file,
            limit=args.limit,
            pull_remote=not args.skip_remote_pull,
            model=args.model,
            page_delay_seconds=args.page_delay_seconds,
            budget_limit_usd=args.budget_limit_usd,
            large_pdf_page_workers=args.large_pdf_page_workers,
            large_pdf_page_threshold=args.large_pdf_page_threshold,
            force=args.force,
        )
    except KeyboardInterrupt:
        print("Interrupted; rerun the same command to resume cached page outputs.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"manifest={(args.out / 'batch_status.json').resolve()}")
    print(f"summary={summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
