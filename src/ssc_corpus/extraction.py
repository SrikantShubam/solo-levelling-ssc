from __future__ import annotations

import json
import copy
import re
import time
import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import numpy as np

from .crops import crop_filename, safe_crop_stem, save_pdf_region_crop
from .extraction_qc import (
    classify_modality,
    decide_correct_answer_evidence,
    review_reasons_for_question,
)
from .mark_detection import detect_green_from_rgb
from .pdf_layout import inspect_pdf_layout


DEFAULT_MODEL = "models/gemini-3.1-flash-lite"

PageFallbackExtractor = Callable[[Path, int, dict[str, Any]], dict[str, Any]]
PageExtractor = Callable[[Path, int], dict[str, Any]]


@dataclass
class ExtractionResult:
    output_dir: Path
    merged_path: Path
    summary_path: Path
    question_count: int
    qc_passed: bool
    qc_status: str
    qc_report_path: Path | None = None
    review_worklist_path: Path | None = None


def render_pdf_pages(pdf_path: Path, image_dir: Path, scale: float = 2.5) -> list[Path]:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required for PDF page rendering") from exc

    image_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf_path))
    paths: list[Path] = []
    for index, page in enumerate(doc, start=1):
        path = image_dir / f"page_{index:02d}.png"
        if not path.exists():
            pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
            pix.save(str(path))
        paths.append(path)
    return paths


def merge_page_results(
    source_pdf: Path,
    page_results: list[dict[str, Any]],
    expected_questions: int | None,
) -> dict[str, Any]:
    questions: list[dict[str, Any]] = []
    page_counts = []
    load_errors = []
    structural_failure_reasons: list[str] = []
    for fallback_page, page_result in enumerate(page_results, start=1):
        page_number = page_result.get("page") or fallback_page
        normalized_page = _normalize_page_result(page_result, page_number)
        warnings = normalized_page.get("warnings") or []
        failure_type = normalized_page.get("failure_type")
        page_status = normalized_page.get("page_status")
        if page_status != "OK":
            load_errors.append(
                {
                    "page": page_number,
                    "warnings": warnings,
                    "failure_type": failure_type,
                    "retryable": normalized_page.get("retryable", False),
                }
            )
            if failure_type:
                structural_failure_reasons.append(str(failure_type))
        page_questions = page_result.get("questions") or []
        page_counts.append(
            {
                "page": page_number,
                "count": len(page_questions),
                "warnings": warnings,
                "page_status": page_status,
                "failure_type": failure_type,
                "retryable": normalized_page.get("retryable", False),
                "provider": normalized_page.get("provider"),
                "model": normalized_page.get("model"),
                "fallback_attempted": normalized_page.get("fallback_attempted", False),
                "fallback_used": normalized_page.get("fallback_used", False),
            }
        )
        for question in page_questions:
            normalized = dict(question)
            normalized["raw_gemini_record"] = copy.deepcopy(question)
            normalized["source_page"] = page_number
            normalized["section_local_question_number"] = normalized.get("question_number")
            normalized["global_question_number"] = len(questions) + 1
            questions.append(normalized)

    option_issues = _option_or_answer_issues(questions)
    chosen_issues = _chosen_answer_issues(questions)
    confidence_issues = [
        q.get("global_question_number")
        for q in questions
        if str(q.get("confidence", "")).lower() in {"low", "manual_review"}
    ]
    for question in questions:
        global_number = question.get("global_question_number")
        manual_reasons = []
        if global_number in chosen_issues:
            manual_reasons.append("missing_or_invalid_chosen_option")
        if global_number in confidence_issues:
            manual_reasons.append("low_confidence")
        question["manual_review"] = bool(manual_reasons)
        question["manual_review_reasons"] = manual_reasons
    if expected_questions is not None and len(questions) != expected_questions:
        structural_failure_reasons.append("expected_question_count_mismatch")
    if option_issues:
        structural_failure_reasons.append("malformed_options_or_correct_answer")
    if expected_questions and not questions and not load_errors:
        structural_failure_reasons.append("true_empty_or_non_question_pdf")
    structural_failure_reasons = list(dict.fromkeys(structural_failure_reasons))
    structural_status = _structural_status(
        question_count=len(questions),
        expected_questions=expected_questions,
        load_errors=load_errors,
        reasons=structural_failure_reasons,
    )
    structural_passed = structural_status == "PASS"
    merged = {
        "source_pdf": str(source_pdf),
        "extraction_method": "Gemini page-by-page visual PNG extraction, merged in page/visual order",
        "page_count": len(page_results),
        "question_count": len(questions),
        "expected_question_count": expected_questions,
        "is_complete_question_trial": expected_questions is None or len(questions) == expected_questions,
        "qc_passed": structural_passed,
        "qc_status": "PASS" if structural_passed else structural_status,
        "structural_status": structural_status,
        "structural_failure_reasons": structural_failure_reasons,
        "page_counts": page_counts,
        "load_errors": load_errors,
        "option_or_correct_answer_issue_global_questions": option_issues,
        "missing_or_invalid_chosen_option_global_questions": chosen_issues,
        "low_confidence_global_questions": confidence_issues,
        "manual_review_count": len(set(chosen_issues + confidence_issues)),
        "questions": questions,
    }
    _enrich_questions(merged)
    _refresh_qc_status(merged)
    return merged


def write_review_summary(merged: dict[str, Any], path: Path) -> None:
    lines = [
        "# Full PDF Visual Extraction",
        "",
        f"- Source PDF: `{merged['source_pdf']}`",
        "- Method: rendered each page to PNG, Gemini visual extraction per page, merged by page order",
        f"- Questions extracted: {merged['question_count']} / {merged.get('expected_question_count')}",
        f"- Overall status: {merged.get('qc_status', 'PASS' if merged['qc_passed'] else 'FAIL')}",
        f"- Structural QC passed: {merged['qc_passed']}",
        f"- Load errors: {merged['load_errors']}",
        "- Option/correct-answer issue global questions: "
        f"{merged['option_or_correct_answer_issue_global_questions']}",
        "- Missing/invalid chosen-option global questions: "
        f"{merged.get('missing_or_invalid_chosen_option_global_questions', [])}",
        f"- Low-confidence global questions: {merged['low_confidence_global_questions']}",
        f"- Manual review count: {merged.get('manual_review_count', 0)}",
        f"- Canonical review count: {merged.get('canonical_review_count', 0)}",
        "",
        "## Gate Summary",
        "",
        "| Check | Status | Count/Detail |",
        "|---|---|---|",
        f"| Page JSON parse | {'PASS' if not merged['load_errors'] else 'FAIL'} | {len(merged['load_errors'])} failures |",
        f"| Expected question count | {'PASS' if merged['is_complete_question_trial'] else 'FAIL'} | {merged['question_count']} / {merged.get('expected_question_count')} |",
        f"| Four options and correct answer | {'PASS' if not merged['option_or_correct_answer_issue_global_questions'] else 'FAIL'} | {merged['option_or_correct_answer_issue_global_questions']} |",
        f"| Chosen answer present/valid | {'PASS' if not merged.get('missing_or_invalid_chosen_option_global_questions') else 'WARN'} | {merged.get('missing_or_invalid_chosen_option_global_questions', [])} |",
        f"| Confidence/manual-review flags | {'PASS' if not merged['low_confidence_global_questions'] else 'WARN'} | {merged['low_confidence_global_questions']} |",
        f"| Canonical review routing | {'PASS' if not merged.get('canonical_review_count') else 'WARN'} | {merged.get('canonical_review_count', 0)} questions |",
        "",
        "## Page Counts",
        "",
        "| Page | Questions |",
        "|---:|---:|",
    ]
    for page_count in merged["page_counts"]:
        lines.append(f"| {page_count['page']} | {page_count['count']} |")
    lines.extend(
        [
            "",
            "## Review Table",
            "",
            "| Global Q | Section Q | Page | Correct | Chosen | Confidence | Manual Review | Short text |",
            "|---:|---:|---:|---|---|---|---|---|",
        ]
    )
    for question in merged["questions"]:
        text = " ".join(str(question.get("question_text_full", "")).split())[:130]
        text = text.replace("|", "/")
        correct = str(question.get("correct_option_label") or "")
        if question.get("correct_option_text"):
            correct += ": " + " ".join(str(question["correct_option_text"]).split())[:45].replace(
                "|", "/"
            )
        lines.append(
            "| {global_q} | {local_q} | {page} | {correct} | {chosen} | {confidence} | {manual} | {text} |".format(
                global_q=question.get("global_question_number", ""),
                local_q=question.get("section_local_question_number", ""),
                page=question.get("source_page", ""),
                correct=correct,
                chosen=question.get("chosen_option_label", ""),
                confidence=question.get("confidence", ""),
                manual=question.get("manual_review", False),
                text=text,
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_extraction_qc_report(merged: dict[str, Any], path: Path) -> None:
    counts = _count_by(merged["questions"], "question_modality")
    evidence_counts = _count_by(merged["questions"], "evidence_status")
    lines = [
        "# Extraction QC Report",
        "",
        f"- Source PDF: `{merged['source_pdf']}`",
        f"- Overall status: {merged['qc_status']}",
        f"- Questions: {merged['question_count']} / {merged.get('expected_question_count')}",
        f"- Structural QC passed: {merged['qc_passed']}",
        f"- Canonical review count: {merged.get('canonical_review_count', 0)}",
        "",
        "## Modality Counts",
        "",
        "| Modality | Count |",
        "|---|---:|",
    ]
    lines.extend([f"| {key} | {value} |" for key, value in sorted(counts.items())])
    lines.extend(["", "## Evidence Counts", "", "| Evidence status | Count |", "|---|---:|"])
    lines.extend([f"| {key} | {value} |" for key, value in sorted(evidence_counts.items())])
    lines.extend(
        [
            "",
            "## Blocking / Review Reasons",
            "",
            "| Global Q | Page | Modality | Evidence | Reasons |",
            "|---:|---:|---|---|---|",
        ]
    )
    for question in merged["questions"]:
        reasons = question.get("canonical_review_reasons") or []
        if reasons:
            lines.append(
                "| {q} | {page} | {modality} | {evidence} | {reasons} |".format(
                    q=question.get("global_question_number", ""),
                    page=question.get("source_page", ""),
                    modality=question.get("question_modality", ""),
                    evidence=question.get("evidence_status", ""),
                    reasons=", ".join(reasons),
                )
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_review_worklist(merged: dict[str, Any], path: Path) -> None:
    lines = [
        "# Extraction Review Worklist",
        "",
        "Only rows with canonical review reasons are listed. Chosen-option-only rows are non-blocking for corpus/archetype extraction.",
        "",
        "| Global Q | Section Q | Page | Modality | Correct | Evidence | Reasons | Page asset | Short text |",
        "|---:|---:|---:|---|---|---|---|---|---|",
    ]
    for question in merged["questions"]:
        reasons = question.get("canonical_review_reasons") or []
        if not reasons:
            continue
        text = " ".join(str(question.get("question_text_full", "")).split())[:120].replace("|", "/")
        lines.append(
            "| {q} | {local} | {page} | {modality} | {correct} | {evidence} | {reasons} | {asset} | {text} |".format(
                q=question.get("global_question_number", ""),
                local=question.get("section_local_question_number", ""),
                page=question.get("source_page", ""),
                modality=question.get("question_modality", ""),
                correct=question.get("correct_option_label", ""),
                evidence=question.get("evidence_status", ""),
                reasons=", ".join(reasons),
                asset=question.get("page_asset_path", ""),
                text=text,
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def extract_pdf_with_gemini(
    pdf_path: Path,
    output_dir: Path,
    api_key: str,
    expected_questions: int | None = 100,
    model_name: str = DEFAULT_MODEL,
    force: bool = False,
    fallback_extractor: PageFallbackExtractor | None = None,
) -> ExtractionResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    image_paths = render_pdf_pages(pdf_path, output_dir / "page_images")
    page_json_dir = output_dir / "page_json"
    page_json_dir.mkdir(parents=True, exist_ok=True)

    model = _build_gemini_model(api_key, model_name)
    page_results = []
    for index, image_path in enumerate(image_paths, start=1):
        json_path = page_json_dir / f"page_{index:02d}.json"
        if json_path.exists() and not force:
            page_results.append(json.loads(json_path.read_text(encoding="utf-8")))
            continue
        page_result = _extract_page(
            model,
            image_path,
            index,
            provider="google_ai_studio",
            model_name=model_name,
            fallback_extractor=fallback_extractor,
        )
        json_path.write_text(json.dumps(page_result, ensure_ascii=False, indent=2), encoding="utf-8")
        page_results.append(page_result)

    return _finalize_extraction_result(
        pdf_path=pdf_path,
        output_dir=output_dir,
        page_results=page_results,
        expected_questions=expected_questions,
        extraction_method="Gemini page-by-page visual PNG extraction, merged in page/visual order",
    )


def extract_pdf_with_openai_compatible_vision(
    pdf_path: Path,
    output_dir: Path,
    *,
    provider: str,
    model_name: str,
    endpoint: str,
    api_key: str,
    expected_questions: int | None = 100,
    force: bool = False,
    fallback_extractor: PageFallbackExtractor | None = None,
    page_delay_seconds: float = 0.0,
) -> ExtractionResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    image_paths = render_pdf_pages(pdf_path, output_dir / "page_images")
    page_json_dir = output_dir / "page_json"
    page_json_dir.mkdir(parents=True, exist_ok=True)

    def page_extractor(image_path: Path, page_number: int) -> dict[str, Any]:
        result = _call_openai_compatible_vision_page(
            provider=provider,
            model_name=model_name,
            endpoint=endpoint,
            api_key=api_key,
            image_path=image_path,
            page_number=page_number,
        )
        if result.get("page_status") == "ERROR" and fallback_extractor:
            return _maybe_run_fallback(result, image_path, page_number, fallback_extractor)
        if page_delay_seconds > 0 and page_number < len(image_paths):
            time.sleep(page_delay_seconds)
        return result

    page_results = _collect_page_results(image_paths, page_json_dir, page_extractor, force=force)
    return _finalize_extraction_result(
        pdf_path=pdf_path,
        output_dir=output_dir,
        page_results=page_results,
        expected_questions=expected_questions,
        extraction_method=f"{provider} {model_name} page-by-page visual PNG extraction, merged in page/visual order",
    )


def read_api_key(env_file: Path, names: tuple[str, ...] = ("GOOGLE_API_KEY", "GEMINI_API_KEY", "api")) -> str:
    text = env_file.read_text(encoding="utf-8", errors="ignore")
    for name in names:
        match = re.search(rf"{re.escape(name)}\s*=\s*[\"']?([^\"'\r\n]+)", text)
        if match:
            return match.group(1).strip()
    raise ValueError(f"No Gemini API key found in {env_file}")


def _build_gemini_model(api_key: str, model_name: str) -> Any:
    try:
        import google.generativeai as genai
    except ImportError as exc:
        raise RuntimeError("google-generativeai is required for Gemini extraction") from exc
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)


def _collect_page_results(
    image_paths: list[Path],
    page_json_dir: Path,
    page_extractor: PageExtractor,
    *,
    force: bool,
) -> list[dict[str, Any]]:
    page_results: list[dict[str, Any]] = []
    for index, image_path in enumerate(image_paths, start=1):
        json_path = page_json_dir / f"page_{index:02d}.json"
        if json_path.exists() and not force:
            page_results.append(json.loads(json_path.read_text(encoding="utf-8")))
            continue
        page_result = page_extractor(image_path, index)
        json_path.write_text(json.dumps(page_result, ensure_ascii=False, indent=2), encoding="utf-8")
        page_results.append(page_result)
    return page_results


def _finalize_extraction_result(
    *,
    pdf_path: Path,
    output_dir: Path,
    page_results: list[dict[str, Any]],
    expected_questions: int | None,
    extraction_method: str,
) -> ExtractionResult:
    raw_page_result_path = output_dir / "raw_page_result.json"
    raw_page_result_path.write_text(json.dumps(page_results, ensure_ascii=False, indent=2), encoding="utf-8")
    merged = merge_page_results(pdf_path, page_results, expected_questions)
    merged["extraction_method"] = extraction_method
    _apply_layout_evidence(merged, pdf_path, output_dir)
    _attach_asset_paths(merged, output_dir)
    _enrich_questions(merged)
    _refresh_qc_status(merged)
    merged_path = output_dir / "merged_questions_global_order.json"
    summary_path = output_dir / "review_summary_global_order.md"
    qc_report_path = output_dir / "extraction_qc_report.md"
    review_worklist_path = output_dir / "review_worklist.md"
    merged_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    write_review_summary(merged, summary_path)
    write_extraction_qc_report(merged, qc_report_path)
    write_review_worklist(merged, review_worklist_path)
    return ExtractionResult(
        output_dir=output_dir,
        merged_path=merged_path,
        summary_path=summary_path,
        question_count=merged["question_count"],
        qc_passed=merged["qc_passed"],
        qc_status=merged["qc_status"],
        qc_report_path=qc_report_path,
        review_worklist_path=review_worklist_path,
    )


def _extract_page(
    model: Any,
    image_path: Path,
    page_number: int,
    *,
    provider: str = "google_ai_studio",
    model_name: str = DEFAULT_MODEL,
    uploader: Callable[[Path], Any] | None = None,
    file_getter: Callable[[Any], Any] | None = None,
    sleep: Callable[[float], None] = time.sleep,
    fallback_extractor: PageFallbackExtractor | None = None,
) -> dict[str, Any]:
    import google.generativeai as genai

    upload = uploader or (lambda path: genai.upload_file(str(path), mime_type="image/png"))
    get_file = file_getter or (lambda uploaded_file: genai.get_file(uploaded_file.name))

    uploaded = upload(image_path)
    for _ in range(20):
        uploaded = get_file(uploaded)
        if str(getattr(uploaded, "state", "")).endswith("ACTIVE"):
            break
        sleep(2)
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            response = model.generate_content(
                [_page_prompt(page_number), uploaded], generation_config={"temperature": 0}
            )
            break
        except Exception as exc:  # API errors should not kill the whole batch.
            last_error = exc
            sleep(2**attempt)
    else:
        failure = _error_page_result(
            page_number=page_number,
            warning=f"ERROR API: {type(last_error).__name__}: {last_error}",
            provider=provider,
            model_name=model_name,
        )
        return _maybe_run_fallback(failure, image_path, page_number, fallback_extractor)
    try:
        text = _strip_json_fences(response.text or "")
    except ValueError as exc:
        failure = _error_page_result(
            page_number=page_number,
            warning=f"ERROR RESPONSE: {type(exc).__name__}: {exc}",
            provider=provider,
            model_name=model_name,
        )
        return _maybe_run_fallback(failure, image_path, page_number, fallback_extractor)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        failure = _error_page_result(
            page_number=page_number,
            warning=f"ERROR JSONDecodeError: {exc}",
            provider=provider,
            model_name=model_name,
            extra_warnings=[text[:2000]],
        )
        return _maybe_run_fallback(failure, image_path, page_number, fallback_extractor)
    data["page"] = page_number
    data.setdefault("questions", [])
    data.setdefault("warnings", [])
    data.setdefault("page_status", "OK")
    data.setdefault("failure_type", None)
    data.setdefault("provider", provider)
    data.setdefault("model", model_name)
    data.setdefault("retryable", False)
    data.setdefault("fallback_attempted", False)
    data.setdefault("fallback_used", False)
    data.setdefault("carrier_used", "gemini_page_image")
    return data


def _call_openai_compatible_vision_page(
    *,
    provider: str,
    model_name: str,
    endpoint: str,
    api_key: str,
    image_path: Path,
    page_number: int,
) -> dict[str, Any]:
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _page_prompt(page_number)},
                    {"type": "image_url", "image_url": {"url": _image_data_url(image_path)}},
                ],
            }
        ],
        "temperature": 0,
    }
    request = Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://local.ssc-corpus",
            "X-Title": "ssc-corpus-extract-pdf",
        },
        method="POST",
    )
    last_error_body = ""
    for attempt in range(6):
        try:
            with urlopen(request, timeout=300) as response:
                data = json.loads(response.read().decode("utf-8"))
            break
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            last_error_body = body[:1000]
            code = exc.code
            if code == 429:
                backoff = 2 ** (attempt + 2)
                time.sleep(backoff)
                continue
            if code >= 500:
                time.sleep(2 ** (attempt + 1))
                continue
            return _error_page_result(
                page_number=page_number,
                warning=f"ERROR HTTP {exc.code}: {body[:1000]}",
                provider=provider,
                model_name=model_name,
                carrier_used=f"{provider}_page_image",
            )
        except URLError as exc:
            if attempt < 5:
                time.sleep(2 ** (attempt + 1))
                continue
            return _error_page_result(
                page_number=page_number,
                warning=f"ERROR URL: {exc}",
                provider=provider,
                model_name=model_name,
                carrier_used=f"{provider}_page_image",
            )
        except TimeoutError as exc:
            if attempt < 5:
                time.sleep(2 ** (attempt + 1))
                continue
            return _error_page_result(
                page_number=page_number,
                warning=f"ERROR TimeoutError: {exc}",
                provider=provider,
                model_name=model_name,
                carrier_used=f"{provider}_page_image",
            )
    else:
        return _error_page_result(
            page_number=page_number,
            warning=f"ERROR HTTP (retries exhausted): {last_error_body[:500]}",
            provider=provider,
            model_name=model_name,
            carrier_used=f"{provider}_page_image",
        )

    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    if isinstance(content, list):
        content = "\n".join(str(item.get("text", item)) for item in content)
    text = _strip_json_fences(str(content))
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        return _error_page_result(
            page_number=page_number,
            warning=f"ERROR JSONDecodeError: {exc}",
            provider=provider,
            model_name=model_name,
            carrier_used=f"{provider}_page_image",
            extra_warnings=[text[:2000]],
        )
    if not isinstance(parsed, dict):
        return _error_page_result(
            page_number=page_number,
            warning=f"ERROR Schema: expected object got {type(parsed).__name__}",
            provider=provider,
            model_name=model_name,
            carrier_used=f"{provider}_page_image",
            extra_warnings=[text[:2000]],
        )
    parsed["page"] = page_number
    parsed.setdefault("questions", [])
    parsed.setdefault("warnings", [])
    parsed.setdefault("page_status", "OK")
    parsed.setdefault("failure_type", None)
    parsed.setdefault("provider", provider)
    parsed.setdefault("model", model_name)
    parsed.setdefault("retryable", False)
    parsed.setdefault("fallback_attempted", False)
    parsed.setdefault("fallback_used", False)
    parsed.setdefault("carrier_used", f"{provider}_page_image")
    return parsed


def _image_data_url(image_path: Path) -> str:
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _normalize_page_result(page_result: dict[str, Any], page_number: int) -> dict[str, Any]:
    normalized = dict(page_result)
    normalized["page"] = page_number
    warning_text = "\n".join(str(item) for item in normalized.get("warnings") or [])
    failure_type = normalized.get("failure_type") or _classify_failure_type(warning_text)
    normalized["failure_type"] = failure_type
    normalized["page_status"] = normalized.get("page_status") or ("ERROR" if failure_type else "OK")
    normalized["retryable"] = bool(normalized.get("retryable", _is_retryable_failure(failure_type)))
    normalized.setdefault("provider", None)
    normalized.setdefault("model", None)
    normalized.setdefault("fallback_attempted", False)
    normalized.setdefault("fallback_used", False)
    return normalized


def _error_page_result(
    *,
    page_number: int,
    warning: str,
    provider: str,
    model_name: str,
    carrier_used: str | None = None,
    extra_warnings: list[str] | None = None,
) -> dict[str, Any]:
    warnings = [warning]
    warnings.extend(extra_warnings or [])
    failure_type = _classify_failure_type("\n".join(warnings))
    return {
        "page": page_number,
        "questions": [],
        "warnings": warnings,
        "page_status": "ERROR",
        "failure_type": failure_type,
        "provider": provider,
        "model": model_name,
        "retryable": _is_retryable_failure(failure_type),
        "fallback_attempted": False,
        "fallback_used": False,
        "carrier_used": carrier_used or f"{provider}_page_image",
    }


def _maybe_run_fallback(
    failure: dict[str, Any],
    image_path: Path,
    page_number: int,
    fallback_extractor: PageFallbackExtractor | None,
) -> dict[str, Any]:
    if not fallback_extractor:
        return failure
    failure["fallback_attempted"] = True
    try:
        fallback = fallback_extractor(image_path, page_number, copy.deepcopy(failure))
    except Exception as exc:
        failure["warnings"].append(f"ERROR FALLBACK: {type(exc).__name__}: {exc}")
        return failure
    fallback.setdefault("page", page_number)
    fallback.setdefault("questions", [])
    fallback.setdefault("warnings", [])
    warning_text = "\n".join(str(item) for item in fallback.get("warnings") or [])
    fallback_failure = fallback.get("failure_type") or _classify_failure_type(warning_text)
    fallback["failure_type"] = fallback_failure
    fallback["page_status"] = fallback.get("page_status") or ("ERROR" if fallback_failure else "OK")
    fallback.setdefault("retryable", False)
    fallback["fallback_attempted"] = True
    fallback["fallback_used"] = fallback.get("page_status") == "OK" and not fallback_failure
    fallback.setdefault("carrier_used", "fallback_page_image")
    fallback.setdefault("fallback_parent_failure_type", failure.get("failure_type"))
    return fallback


def _classify_failure_type(text: str) -> str | None:
    lowered = text.lower()
    if not lowered:
        return None
    if "resourceexhausted" in lowered or "429" in lowered or "quota" in lowered or "rate limit" in lowered:
        return "api_quota_or_rate_limit"
    if "timeouterror" in lowered or "timed out" in lowered:
        return "provider_timeout"
    if "finish_reason" in lowered or "copyright" in lowered or "reciting from copyrighted" in lowered:
        return "model_refusal"
    if "jsondecodeerror" in lowered or "schema" in lowered or "malformed" in lowered:
        return "json_or_schema_failure"
    if "degraded function cannot be invoked" in lowered or "provider unavailable" in lowered:
        return "fallback_provider_unavailable"
    if "error" in lowered:
        return "layout_class_unsupported"
    return None


def _is_retryable_failure(failure_type: str | None) -> bool:
    return failure_type in {"api_quota_or_rate_limit", "json_or_schema_failure", "provider_timeout"}


def _structural_status(
    *,
    question_count: int,
    expected_questions: int | None,
    load_errors: list[dict[str, Any]],
    reasons: list[str],
) -> str:
    if not reasons:
        return "PASS"
    infra_reasons = {"api_quota_or_rate_limit", "model_refusal", "json_or_schema_failure", "provider_timeout"}
    if load_errors and any(reason in infra_reasons for reason in reasons):
        return "INFRA_FAILURE"
    if expected_questions and question_count == 0:
        return "QUARANTINE"
    return "FAIL"


def _page_prompt(page_number: int) -> str:
    return f"""Extract every question visible on this single rendered SSC page.
Return STRICT JSON only. Schema:
{{"page":{page_number},"questions":[{{"question_number":integer|null,"section":string|null,"question_text_full":string,"options":[{{"label":"1","text":string}},{{"label":"2","text":string}},{{"label":"3","text":string}},{{"label":"4","text":string}}],"question_id":string|null,"chosen_option_label":string|null,"correct_option_label":string|null,"correct_option_text":string|null,"is_complete_on_page":boolean,"confidence":"high"|"medium"|"low","notes":string}}],"warnings":[]}}
Rules:
- Correct option is the GREEN tick/check-marked option, not necessarily Chosen Option.
- Chosen Option is the response-sheet field; keep it separate.
- Red cross is not correct.
- Do not truncate question text.
- Extract all four option texts whenever visible. If an option is a figure, write Figure 1, Figure 2, etc.
- In SSC pages, answer choices are the four items under the visible "Ans" block with red/green marks.
- Do not treat numbered items inside the question stem as answer options. Example: dictionary-order questions may list words 1-5 inside the stem, but the answer options are still the four sequences under "Ans".
- Every extracted question must have exactly four answer options labeled "1", "2", "3", "4".
- Preserve visual top-to-bottom order.
- No markdown fences. JSON only."""


def _strip_json_fences(text: str) -> str:
    stripped = text.strip()
    stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
    stripped = re.sub(r"\s*```$", "", stripped)
    return stripped


def _option_or_answer_issues(questions: list[dict[str, Any]]) -> list[int | None]:
    issues = []
    for question in questions:
        options = question.get("options") or []
        labels = [str(option.get("label")) for option in options if isinstance(option, dict)]
        correct = str(question.get("correct_option_label"))
        if labels != ["1", "2", "3", "4"] or correct not in {"1", "2", "3", "4"}:
            issues.append(question.get("global_question_number"))
    return issues


def _chosen_answer_issues(questions: list[dict[str, Any]]) -> list[int | None]:
    issues = []
    for question in questions:
        chosen = question.get("chosen_option_label")
        if chosen is None or str(chosen).strip() not in {"1", "2", "3", "4"}:
            issues.append(question.get("global_question_number"))
    return issues


def _enrich_questions(merged: dict[str, Any]) -> None:
    option_issue_set = set(merged.get("option_or_correct_answer_issue_global_questions", []))
    chosen_issue_set = set(merged.get("missing_or_invalid_chosen_option_global_questions", []))
    low_confidence_set = set(merged.get("low_confidence_global_questions", []))
    validate_assets = bool(merged.get("asset_evidence_attached"))
    for question in merged["questions"]:
        raw_record = question.get("raw_gemini_record") if isinstance(question.get("raw_gemini_record"), dict) else {}
        raw_correct_label = raw_record.get("correct_option_label", question.get("correct_option_label"))
        raw_correct_text = raw_record.get("correct_option_text", question.get("correct_option_text"))
        question["raw_gemini_correct_option_label"] = raw_correct_label
        question["raw_gemini_correct_option_text"] = raw_correct_text
        options = [
            str(option.get("text", ""))
            for option in question.get("options", [])
            if isinstance(option, dict)
        ]
        modality = classify_modality(str(question.get("question_text_full", "")), options)
        question["question_modality"] = modality.label
        question["question_modality_keywords"] = list(modality.matched_keywords)
        question["visual_required"] = modality.label in {
            "visual_stimulus",
            "visual_options",
            "table_di",
            "graph_chart",
            "dice",
        }
        question["table_required"] = modality.label in {"table_di", "graph_chart"}
        question["math_required"] = modality.label == "math_formula"
        question.setdefault("correct_evidence_source", "llm_only")
        question.setdefault("deterministic_correct_option_label", None)
        evidence = decide_correct_answer_evidence(
            gemini_label=raw_correct_label,
            deterministic_label=question.get("deterministic_correct_option_label"),
            simple_text_only=modality.label == "text_only",
        )
        question["evidence_status"] = evidence.status
        question["evidence_reasons"] = list(evidence.reasons)
        _apply_canonical_answer(question, evidence)
        review_reasons = review_reasons_for_question(
            modality=modality.label,
            evidence_status=evidence.status,
            chosen_missing=question.get("global_question_number") in chosen_issue_set,
            option_issue=question.get("global_question_number") in option_issue_set,
            low_confidence=question.get("global_question_number") in low_confidence_set,
            has_page_asset=True if not validate_assets else bool(question.get("page_asset_path")),
            has_visual_asset=True
            if not validate_assets
            else bool(question.get("stimulus_crop_path") or question.get("question_crop_path")),
            has_question_crop=True if not validate_assets else bool(question.get("question_crop_path")),
        )
        question["canonical_review_reasons"] = list(review_reasons)
        question["practice_ready"] = _is_practice_ready(question)


def _attach_asset_paths(merged: dict[str, Any], output_dir: Path) -> None:
    merged["asset_evidence_attached"] = True
    for question in merged["questions"]:
        page = int(question.get("source_page") or 0)
        page_asset = output_dir / "page_images" / f"page_{page:02d}.png"
        question["page_asset_path"] = str(page_asset)
        question.setdefault("question_crop_path", str(page_asset))
        if question.get("visual_required") or question.get("table_required") or question.get("math_required"):
            question.setdefault("stimulus_crop_path", str(page_asset))
        question.setdefault("option_crop_paths", [])
        question["practice_ready"] = _is_practice_ready(question)


def _apply_layout_evidence(merged: dict[str, Any], pdf_path: Path, output_dir: Path) -> None:
    try:
        layouts = {layout.page_number: layout for layout in inspect_pdf_layout(pdf_path)}
    except Exception as exc:
        merged["layout_evidence_error"] = f"{type(exc).__name__}: {exc}"
        return

    positions_by_page: dict[int, int] = {}
    for question in merged["questions"]:
        page = int(question.get("source_page") or 0)
        positions_by_page[page] = positions_by_page.get(page, 0) + 1
        page_position = positions_by_page[page] - 1
        layout = layouts.get(page)
        if not layout or page_position >= len(layout.question_regions):
            question["correct_evidence_source"] = "unavailable"
            question.setdefault("deterministic_correct_option_label", None)
            question.setdefault("option_crop_paths", [])
            question.setdefault("crop_metadata", [])
            continue

        region = layout.question_regions[page_position]
        page_image_path = output_dir / "page_images" / f"page_{page:02d}.png"
        assets_dir = output_dir / "assets" / "question_crops"
        global_q = int(question.get("global_question_number") or 0)
        question_stem = safe_crop_stem(
            pdf_path.stem,
            page_number=page,
            question_number=global_q,
            suffix="question",
        )
        question_crop_path = assets_dir / crop_filename(question_stem)
        question_crop = save_pdf_region_crop(
            page_image_path=page_image_path,
            page_rect=layout.page_rect,
            bbox=region.question_bbox,
            output_path=question_crop_path,
            page_number=page,
            question_number=global_q,
        )
        question["question_crop_path"] = str(question_crop_path)
        question.setdefault("crop_metadata", []).append(question_crop.to_dict())

        option_crop_paths: list[str] = []
        option_results: dict[str, dict[str, Any]] = {}
        green_labels: list[str] = []
        for option in region.option_regions:
            option_stem = safe_crop_stem(
                pdf_path.stem,
                page_number=page,
                question_number=global_q,
                option_label=option.label,
                suffix="option",
            )
            option_crop_path = assets_dir / crop_filename(option_stem)
            option_crop = save_pdf_region_crop(
                page_image_path=page_image_path,
                page_rect=layout.page_rect,
                bbox=option.bbox,
                output_path=option_crop_path,
                page_number=page,
                question_number=global_q,
                option_label=option.label,
            )
            option_crop_paths.append(str(option_crop_path))
            question["crop_metadata"].append(option_crop.to_dict())
            result = _detect_green_in_crop(option_crop_path)
            option_results[option.label] = result.to_dict()
            if result.label == "green_mark_present":
                green_labels.append(option.label)

        question["option_crop_paths"] = option_crop_paths
        question["deterministic_option_evidence"] = option_results
        if len(green_labels) == 1:
            question["deterministic_correct_option_label"] = green_labels[0]
            question["correct_evidence_source"] = "rgb_hsv_option_crop"
        else:
            question["deterministic_correct_option_label"] = "AMBIGUOUS" if green_labels else None
            question["correct_evidence_source"] = "unavailable" if not green_labels else "ambiguous_rgb_hsv_option_crop"


def _detect_green_in_crop(crop_path: Path) -> Any:
    from PIL import Image

    with Image.open(crop_path) as image:
        return detect_green_from_rgb(np.array(image.convert("RGB")), min_green_fraction=0.002)


def _apply_canonical_answer(question: dict[str, Any], evidence: Any) -> None:
    if evidence.status == "PASS_WITH_EVIDENCE":
        canonical = evidence.deterministic_label or evidence.gemini_label
    elif evidence.status == "PASS_LLM_ONLY":
        canonical = evidence.gemini_label
    else:
        canonical = None

    question["canonical_correct_option_label"] = canonical
    if canonical:
        question["correct_option_label"] = canonical
        question["correct_option_text"] = _option_text_for_label(question, canonical)
    else:
        question["correct_option_label"] = None
        question["correct_option_text"] = None


def _option_text_for_label(question: dict[str, Any], label: str) -> str | None:
    for option in question.get("options") or []:
        if isinstance(option, dict) and str(option.get("label")) == str(label):
            return str(option.get("text") or "")
    return None


def _is_practice_ready(question: dict[str, Any]) -> bool:
    if question.get("blocking_review_reasons"):
        return False
    if not question.get("canonical_correct_option_label"):
        return False
    if question.get("visual_required"):
        if question.get("question_modality") == "visual_options":
            return len(question.get("option_crop_paths") or []) == 4
        return bool(question.get("stimulus_crop_path") or question.get("question_crop_path"))
    if question.get("math_required"):
        return bool(question.get("question_crop_path"))
    return True


def _refresh_qc_status(merged: dict[str, Any]) -> None:
    structural_passed = bool(merged.get("qc_passed"))
    for question in merged["questions"]:
        reasons = question.get("canonical_review_reasons") or []
        # Chosen-option gaps are useful for response analytics but not blocking for corpus truth.
        blocking_reasons = [reason for reason in reasons if reason != "chosen_option_missing"]
        question["blocking_review_reasons"] = blocking_reasons
    blocking_count = sum(1 for question in merged["questions"] if question["blocking_review_reasons"])
    review_count = sum(1 for question in merged["questions"] if question.get("canonical_review_reasons"))
    merged["canonical_review_count"] = review_count
    merged["blocking_review_count"] = blocking_count
    if not structural_passed or blocking_count:
        merged["qc_status"] = "BLOCKED" if structural_passed else merged.get("structural_status", "FAIL")
    elif review_count:
        merged["qc_status"] = "PASS_WITH_MANUAL_REVIEW"
    else:
        statuses = {question.get("evidence_status") for question in merged["questions"]}
        merged["qc_status"] = "PASS_LLM_ONLY" if statuses == {"PASS_LLM_ONLY"} else "PASS"


def _count_by(questions: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for question in questions:
        value = str(question.get(key) or "unknown")
        counts[value] = counts.get(value, 0) + 1
    return counts
