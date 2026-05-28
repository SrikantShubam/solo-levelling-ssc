from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class NativeComparisonOutputs:
    pipeline_1_path: Path
    pipeline_2_path: Path
    audit_path: Path


def generate_native_two_pipeline_comparison(run_dir: Path) -> NativeComparisonOutputs:
    return generate_native_two_pipeline_comparison_from_runs(
        pipeline_1_run_dir=run_dir,
        pipeline_2_run_dir=run_dir,
        output_dir=run_dir,
        pipeline_1_source_status="cached",
        pipeline_2_source_status="cached existing merged artifact",
        fallback_model_used="no",
    )


def generate_native_two_pipeline_comparison_from_runs(
    *,
    pipeline_1_run_dir: Path,
    pipeline_2_run_dir: Path,
    output_dir: Path,
    pipeline_1_source_status: str,
    pipeline_2_source_status: str,
    fallback_model_used: str,
) -> NativeComparisonOutputs:
    page_json_dir = pipeline_1_run_dir / "page_json"
    merged_path = pipeline_2_run_dir / "merged_questions_global_order.json"
    if not page_json_dir.is_dir():
        raise FileNotFoundError(f"Missing page_json directory: {page_json_dir}")
    if not merged_path.exists():
        raise FileNotFoundError(f"Missing merged file: {merged_path}")

    page_payloads = _load_page_payloads(page_json_dir)
    merged_payload = json.loads(merged_path.read_text(encoding="utf-8"))

    pipeline_1 = _build_pipeline_1_from_page_json(pipeline_1_run_dir, page_payloads)
    pipeline_2 = _build_pipeline_2_from_merged(merged_payload)

    output_dir.mkdir(parents=True, exist_ok=True)
    pipeline_1_path = output_dir / "pipeline_1_llm_only_native.json"
    pipeline_2_path = output_dir / "pipeline_2_precision_native.json"
    audit_path = output_dir / "native_pipeline_comparison_audit.md"

    pipeline_1_path.write_text(json.dumps(pipeline_1, indent=2), encoding="utf-8")
    pipeline_2_path.write_text(json.dumps(pipeline_2, indent=2), encoding="utf-8")
    audit_path.write_text(
        _build_audit_text(
            page_json_count=len(page_payloads),
            pipeline_1_run_dir=pipeline_1_run_dir,
            pipeline_2_run_dir=pipeline_2_run_dir,
            pipeline_2_merged_path=merged_path,
            pipeline_1_rows=len(pipeline_1["questions"]),
            pipeline_2_rows=len(pipeline_2["questions"]),
            pipeline_1_source_status=pipeline_1_source_status,
            pipeline_2_source_status=pipeline_2_source_status,
            fallback_model_used=fallback_model_used,
        ),
        encoding="utf-8",
    )
    return NativeComparisonOutputs(
        pipeline_1_path=pipeline_1_path,
        pipeline_2_path=pipeline_2_path,
        audit_path=audit_path,
    )


def _load_page_payloads(page_json_dir: Path) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for path in sorted(page_json_dir.glob("page_*.json")):
        payloads.append(json.loads(path.read_text(encoding="utf-8")))
    if not payloads:
        raise ValueError(f"No page_*.json files found in {page_json_dir}")
    return payloads


def _build_pipeline_1_from_page_json(run_dir: Path, page_payloads: list[dict[str, Any]]) -> dict[str, Any]:
    questions: list[dict[str, Any]] = []
    global_q = 1
    for page_payload in page_payloads:
        page_number = int(page_payload["page"])
        for section_q, q in enumerate(page_payload.get("questions", []), start=1):
            question_number = q.get("question_number")
            questions.append(
                {
                    "global_question_number": global_q,
                    "source_page": page_number,
                    "section_local_question_number": question_number if question_number is not None else section_q,
                    "source": "page_json_cached_native",
                    "pipeline": "pipeline_1_llm_only_native",
                    "native_extraction": {
                        "question_number": q.get("question_number"),
                        "section": q.get("section"),
                        "question_id": q.get("question_id"),
                        "question_text_full": q.get("question_text_full"),
                        "options": q.get("options", []),
                        "chosen_option_label": q.get("chosen_option_label"),
                        "correct_option_label": q.get("correct_option_label"),
                        "correct_option_text": q.get("correct_option_text"),
                        "is_complete_on_page": q.get("is_complete_on_page"),
                        "confidence": q.get("confidence"),
                        "notes": q.get("notes", ""),
                    },
                    "answer": {
                        "raw_gemini_correct_option_label": q.get("correct_option_label"),
                        "raw_gemini_correct_option_text": q.get("correct_option_text"),
                        "evidence_status": "UNVERIFIED_RAW_LLM",
                        "correct_evidence_source": "llm_only",
                    },
                    "native_capabilities": {
                        "uses_deterministic_green_detection": False,
                        "uses_option_crops": False,
                        "uses_visual_asset_validation": False,
                        "uses_precision_qc": False,
                    },
                    "manual_review_assets_added_posthoc": {
                        "page_asset_path": _page_asset_path(run_dir, page_number),
                        "question_crop_path": _question_crop_path(run_dir, page_number, global_q),
                        "stimulus_crop_path": _page_asset_path(run_dir, page_number),
                        "option_crop_paths": _option_crop_paths(run_dir, page_number, global_q),
                    },
                }
            )
            global_q += 1
    return {
        "pipeline": "pipeline_1_llm_only_native",
        "status": "deprecated",
        "source": "page_json/*.json",
        "question_count": len(questions),
        "questions": questions,
    }


def _build_pipeline_2_from_merged(merged_payload: dict[str, Any]) -> dict[str, Any]:
    questions: list[dict[str, Any]] = []
    for q in merged_payload.get("questions", []):
        questions.append(
            {
                "global_question_number": q.get("global_question_number"),
                "source_page": q.get("source_page"),
                "section_local_question_number": q.get("section_local_question_number"),
                "source": "merged_questions_global_order.json",
                "pipeline": "pipeline_2_precision_native",
                "question": {
                    "question_number": q.get("question_number"),
                    "section": q.get("section"),
                    "question_id": q.get("question_id"),
                    "question_text_full": q.get("question_text_full"),
                    "options": q.get("options", []),
                    "chosen_option_label": q.get("chosen_option_label"),
                    "is_complete_on_page": q.get("is_complete_on_page"),
                    "confidence": q.get("confidence"),
                    "notes": q.get("notes", ""),
                },
                "answer": {
                    "raw_gemini_correct_option_label": q.get("raw_gemini_correct_option_label"),
                    "raw_gemini_correct_option_text": q.get("raw_gemini_correct_option_text"),
                    "canonical_correct_option_label": q.get("canonical_correct_option_label"),
                    "deterministic_correct_option_label": q.get("deterministic_correct_option_label"),
                    "correct_evidence_source": q.get("correct_evidence_source"),
                    "evidence_status": q.get("evidence_status"),
                    "evidence_reasons": q.get("evidence_reasons", []),
                    "deterministic_option_evidence": q.get("deterministic_option_evidence", {}),
                },
                "review": {
                    "manual_review_reasons": q.get("manual_review_reasons", []),
                    "canonical_review_reasons": q.get("canonical_review_reasons", []),
                    "blocking_review_reasons": q.get("blocking_review_reasons", []),
                },
                "native_assets": {
                    "page_asset_path": q.get("page_asset_path"),
                    "question_crop_path": q.get("question_crop_path"),
                    "stimulus_crop_path": q.get("stimulus_crop_path") or q.get("question_crop_path"),
                    "option_crop_paths": q.get("option_crop_paths", []),
                },
            }
        )
    return {
        "pipeline": "pipeline_2_precision_native",
        "source": "merged_questions_global_order.json",
        "question_count": len(questions),
        "questions": questions,
    }


def _page_asset_path(run_dir: Path, page_number: int) -> str:
    return str(run_dir / "page_images" / f"page_{page_number:02d}.png")


def _question_crop_path(run_dir: Path, page_number: int, global_q: int) -> str:
    return str(
        run_dir
        / "assets"
        / "question_crops"
        / f"{run_dir.name}_p{page_number:02d}_q{global_q:03d}_question.png"
    )


def _option_crop_paths(run_dir: Path, page_number: int, global_q: int) -> list[str]:
    base = run_dir / "assets" / "question_crops"
    return [
        str(base / f"{run_dir.name}_p{page_number:02d}_q{global_q:03d}_opt_{idx}_option.png")
        for idx in range(1, 5)
    ]


def _build_audit_text(
    *,
    page_json_count: int,
    pipeline_1_run_dir: Path,
    pipeline_2_run_dir: Path,
    pipeline_2_merged_path: Path,
    pipeline_1_rows: int,
    pipeline_2_rows: int,
    pipeline_1_source_status: str,
    pipeline_2_source_status: str,
    fallback_model_used: str,
) -> str:
    return "\n".join(
        [
            "# Native Pipeline Comparison Audit",
            "",
            "## Status",
            "- Pipeline 1 is deprecated for corpus generation and retained only for historical/manual comparison.",
            "- Pipeline 2 is the active extraction path.",
            "",
            "## Input Status",
            f"- Pipeline 1 run dir: `{pipeline_1_run_dir}`",
            f"- Pipeline 1 source (`page_json/*.json`): {pipeline_1_source_status} ({page_json_count} files)",
            f"- Pipeline 2 run dir: `{pipeline_2_run_dir}`",
            f"- Pipeline 2 source (`{pipeline_2_merged_path.name}`): {pipeline_2_source_status}",
            "",
            "## Model Routing",
            f"- Fallback model used: {fallback_model_used}",
            "",
            "## Row Counts",
            f"- Pipeline 1 rows: {pipeline_1_rows}",
            f"- Pipeline 2 rows: {pipeline_2_rows}",
            "",
        ]
    )
