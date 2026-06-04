from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .extraction import _is_practice_ready, _refresh_qc_status


def scan_flagged_questions(pipeline_root: str | Path) -> list[dict[str, Any]]:
    pipeline_root = Path(pipeline_root)
    items: list[dict[str, Any]] = []
    for merged_path in sorted(pipeline_root.rglob("merged_questions_global_order.json")):
        pdf_name = merged_path.parent.name
        data = json.loads(merged_path.read_text(encoding="utf-8"))
        for q in data.get("questions", []):
            if not q.get("practice_ready", False):
                page = q.get("source_page") or 0
                page_image = merged_path.parent / "page_images" / f"page_{int(page):02d}.png"
                items.append({
                    "pdf_name": pdf_name,
                    "page_number": int(page),
                    "merged_path": str(merged_path),
                    "page_image_path": str(page_image) if page_image.exists() else None,
                    "question_number": q.get("question_number"),
                    "global_question_number": q.get("global_question_number"),
                })
    return items


def build_work_manifest(pipeline_root: str | Path, output_path: str | Path | None = None) -> list[dict[str, Any]]:
    items = scan_flagged_questions(pipeline_root)
    pages_seen: set[tuple[str, int]] = set()
    manifest: list[dict[str, Any]] = []
    for item in items:
        key = (item["pdf_name"], item["page_number"])
        if key not in pages_seen and item["page_image_path"]:
            pages_seen.add(key)
            manifest.append({
                "pdf_name": item["pdf_name"],
                "page_number": item["page_number"],
                "page_image_path": item["page_image_path"],
            })
    if output_path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps({
            "total_items": len(items),
            "unique_pages": len(manifest),
            "pages": manifest,
        }, indent=2), encoding="utf-8")
    return manifest


def merge_grok_results(results_path: str | Path, report_path: str | Path | None = None) -> dict[str, Any]:
    results_path = Path(results_path)
    data = json.loads(results_path.read_text(encoding="utf-8"))
    results_list = data if isinstance(data, list) else data.get("results", [])

    stats = {
        "pages_processed": 0,
        "pages_with_results": 0,
        "questions_updated": 0,
        "correct_labels_fixed": 0,
        "chosen_labels_fixed": 0,
        "confidence_fixed": 0,
        "options_fixed": 0,
    }
    pdf_updates: dict[str, dict[str, Any]] = {}

    for page_item in results_list:
        pdf_name = page_item.get("pdf_name") or page_item.get("metadata", {}).get("pdf_name", "unknown")
        page_number = page_item.get("page_number") or page_item.get("metadata", {}).get("page_number", 0)
        merged_path_str = page_item.get("merged_path") or page_item.get("metadata", {}).get("merged_path", "")
        if not merged_path_str:
            continue
        merged_path = Path(merged_path_str)
        if not merged_path.exists():
            continue

        stats["pages_processed"] += 1
        grok_output = page_item.get("grok_output") or page_item.get("output", "")
        if not grok_output:
            continue

        import re
        raw = grok_output
        start_marker = "---SUBAGENT-HANDOFF---"
        s = raw.find(start_marker)
        if s != -1:
            raw = raw[:s]
        end_marker = "---END-HANDOFF---"
        e = raw.find(end_marker)
        if e != -1:
            raw = raw[:e]
        raw = raw.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        grok_data = None
        try:
            grok_data = json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", raw)
            if match:
                try:
                    grok_data = json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass

        if not grok_data or not isinstance(grok_data, dict):
            continue

        stats["pages_with_results"] += 1
        grok_questions = grok_data.get("questions", [])

        merged = json.loads(merged_path.read_text(encoding="utf-8"))
        questions = merged.get("questions", [])
        page_updated = False

        for q in questions:
            eq_num = q.get("question_number")
            gq = None
            for g in grok_questions:
                if g.get("question_number") == eq_num:
                    gq = g
                    break
            if gq is None:
                continue

            changes = {}

            if not q.get("canonical_correct_option_label"):
                grok_correct = gq.get("correct_option_label")
                if grok_correct and str(grok_correct) in {"1", "2", "3", "4"}:
                    changes["canonical_correct_option_label"] = str(grok_correct)
                    changes["correct_option_label"] = str(grok_correct)
                    changes["correct_option_text"] = _find_option_text(gq.get("options", []), str(grok_correct))
                    changes["correct_evidence_source"] = "grok_ai_review"
                    changes["evidence_status"] = "PASS_WITH_EVIDENCE"
                    changes["evidence_reasons"] = ["grok_ai_review"]
                    changes["raw_gemini_correct_option_label"] = q.get("raw_gemini_correct_option_label") or str(grok_correct)
                    stats["correct_labels_fixed"] += 1

            if not q.get("chosen_option_label"):
                grok_chosen = gq.get("chosen_option_label")
                if grok_chosen and str(grok_chosen) in {"1", "2", "3", "4"}:
                    changes["chosen_option_label"] = str(grok_chosen)
                    stats["chosen_labels_fixed"] += 1

            if q.get("confidence") == "low":
                grok_conf = gq.get("confidence")
                if grok_conf and grok_conf in {"high", "medium"}:
                    changes["confidence"] = grok_conf
                    stats["confidence_fixed"] += 1

            existing_opts = q.get("options", [])
            grok_opts = gq.get("options", [])
            existing_texts = {str(o.get("label")): str(o.get("text", "")) for o in existing_opts if isinstance(o, dict)}
            grok_texts = {str(o.get("label")): str(o.get("text", "")) for o in grok_opts if isinstance(o, dict)}
            has_better = False
            for lbl in {"1", "2", "3", "4"}:
                if grok_texts.get(lbl, "") and not existing_texts.get(lbl, ""):
                    has_better = True
                    break
            if has_better:
                new_opts = []
                for lbl in {"1", "2", "3", "4"}:
                    new_opts.append({"label": lbl, "text": grok_texts.get(lbl, "") or existing_texts.get(lbl, "")})
                changes["options"] = new_opts
                stats["options_fixed"] += 1

            if changes:
                changes["ai_reviewed"] = True
                changes["ai_review_source"] = "grok"
                q.update(changes)
                page_updated = True
                stats["questions_updated"] += 1

        if page_updated:
            for q in questions:
                q["practice_ready"] = _is_practice_ready(q)
            _refresh_qc_status(merged)
            merged_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
            pdf_updates[pdf_name] = {
                "merged_path": str(merged_path),
                "qc_status": merged.get("qc_status"),
                "question_count": len(questions),
                "practice_ready": sum(1 for q in questions if q.get("practice_ready")),
            }

    if report_path:
        report = Path(report_path)
        report.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# AI Review Merge Report\n"]
        lines.append(f"- Pages processed: {stats['pages_processed']}\n")
        lines.append(f"- Pages with parseable results: {stats['pages_with_results']}\n")
        lines.append(f"- Questions updated: {stats['questions_updated']}\n")
        lines.append(f"- Correct labels fixed: {stats['correct_labels_fixed']}\n")
        lines.append(f"- Chosen labels fixed: {stats['chosen_labels_fixed']}\n")
        lines.append(f"- Confidence fixed: {stats['confidence_fixed']}\n")
        lines.append(f"- Options fixed: {stats['options_fixed']}\n\n")
        lines.append("## Per-PDF Updates\n")
        for pdf_name, info in sorted(pdf_updates.items()):
            lines.append(f"- {pdf_name}: qc={info['qc_status']}, "
                         f"questions={info['question_count']}, "
                         f"practice_ready={info['practice_ready']}\n")
        report.write_text("".join(lines), encoding="utf-8")

    return stats


def generate_mainfest_report(pipeline_root: str | Path) -> dict[str, Any]:
    items = scan_flagged_questions(pipeline_root)
    pages_seen: set[tuple[str, int]] = set()
    pdf_page_counts: dict[str, int] = {}
    for item in items:
        key = (item["pdf_name"], item["page_number"])
        if key not in pages_seen and item["page_image_path"]:
            pages_seen.add(key)
            pdf_page_counts[item["pdf_name"]] = pdf_page_counts.get(item["pdf_name"], 0) + 1
    return {
        "total_flagged_questions": len(items),
        "unique_pages": len(pages_seen),
        "pages_by_pdf": pdf_page_counts,
    }


def compute_delta(pipeline_root: str | Path) -> dict[str, Any]:
    pipeline_root = Path(pipeline_root)
    practice_ready = 0
    total = 0
    for merged_path in sorted(pipeline_root.rglob("merged_questions_global_order.json")):
        data = json.loads(merged_path.read_text(encoding="utf-8"))
        for q in data.get("questions", []):
            total += 1
            if q.get("practice_ready", False):
                practice_ready += 1
    ai_reviewed = 0
    for merged_path in sorted(pipeline_root.rglob("merged_questions_global_order.json")):
        data = json.loads(merged_path.read_text(encoding="utf-8"))
        for q in data.get("questions", []):
            if q.get("ai_reviewed"):
                ai_reviewed += 1
    return {
        "total_questions": total,
        "practice_ready": practice_ready,
        "ai_reviewed": ai_reviewed,
        "needs_review": total - practice_ready,
    }


def _find_option_text(options: list[dict[str, Any]], label: str) -> str | None:
    for opt in options:
        if str(opt.get("label")) == label:
            return str(opt.get("text") or "")
    return None
