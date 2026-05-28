from __future__ import annotations

import argparse
import json
from pathlib import Path

from .acquisition import acquire_from_seed
from .batch_retry import retry_failed_extractions
from .extraction import (
    DEFAULT_MODEL,
    extract_pdf_with_gemini,
    extract_pdf_with_openai_compatible_vision,
    read_api_key,
)
from .extraction_investigation import (
    build_extraction_investigation,
    write_extraction_investigation_report,
)
from .integrity import audit_workspace
from .model_compare import compare_models
from .model_compare import (
    ModelSpec,
    NVIDIA_NIM_URL,
    _call_openai_compatible_vision,
    _first_env_value,
    _read_env,
)
from .reporting_compare import build_phase_comparison, write_phase_comparison
from .storage import initialize_workspace


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ssc-corpus")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--root", default=".", type=Path)

    acquire_parser = subparsers.add_parser("acquire")
    acquire_parser.add_argument("--root", default=".", type=Path)
    acquire_parser.add_argument("--seed", required=True, type=Path)

    audit_parser = subparsers.add_parser("audit")
    audit_parser.add_argument("--root", default=".", type=Path)

    extract_parser = subparsers.add_parser("extract-pdf")
    extract_parser.add_argument("--pdf", required=True, type=Path)
    extract_parser.add_argument("--out", required=True, type=Path)
    extract_parser.add_argument("--env-file", default=Path(".env.txt"), type=Path)
    extract_parser.add_argument("--model", default=DEFAULT_MODEL)
    extract_parser.add_argument("--provider", choices=["gemini", "nvidia_nim", "openrouter"], default="gemini")
    extract_parser.add_argument("--expected-questions", default=100, type=int)
    extract_parser.add_argument("--force", action="store_true")
    extract_parser.add_argument("--allow-fallback", action="store_true")
    extract_parser.add_argument("--fallback-model", default="microsoft/phi-4-multimodal-instruct")

    compare_parser = subparsers.add_parser("compare-models")
    compare_parser.add_argument("--env-file", default=Path(".env.txt"), type=Path)
    compare_parser.add_argument("--reference", required=True, type=Path)
    compare_parser.add_argument("--image-dir", required=True, type=Path)
    compare_parser.add_argument("--out", required=True, type=Path)
    compare_parser.add_argument("--pages", nargs="+", type=int, default=[1, 5, 17, 28])
    compare_parser.add_argument("--force", action="store_true")

    investigate_parser = subparsers.add_parser("investigate-extraction")
    investigate_parser.add_argument("--batch-summary", required=True, type=Path)
    investigate_parser.add_argument("--out", required=True, type=Path)

    retry_parser = subparsers.add_parser("retry-failed-batch")
    retry_parser.add_argument("--batch-summary", required=True, type=Path)
    retry_parser.add_argument("--investigation", type=Path)
    retry_parser.add_argument("--out", required=True, type=Path)
    retry_parser.add_argument("--env-file", default=Path(".env"), type=Path)
    retry_parser.add_argument("--provider", choices=["gemini", "nvidia_nim", "openrouter"], default="nvidia_nim")
    retry_parser.add_argument("--model", default="mistralai/mistral-medium-3.5-128b")
    retry_parser.add_argument("--force", action="store_true")

    compare_phase_parser = subparsers.add_parser("compare-phases")
    compare_phase_parser.add_argument("--out-md", required=True, type=Path)
    compare_phase_parser.add_argument("--out-json", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = args.root.resolve() if hasattr(args, "root") else Path(".").resolve()

    if args.command == "init":
        initialize_workspace(root)
        return 0
    if args.command == "acquire":
        initialize_workspace(root)
        return acquire_from_seed(root, args.seed.resolve())
    if args.command == "audit":
        result = audit_workspace(root)
        return 0 if result.status == "GO" else 1 if result.status == "GO_WITH_EXCEPTIONS" else 2
    if args.command == "extract-pdf":
        api_key = read_api_key(args.env_file.resolve()) if args.provider == "gemini" else None
        env = _read_env(args.env_file.resolve())
        fallback_extractor = None
        if args.allow_fallback:
            spec = ModelSpec(
                provider="nvidia_nim",
                model=args.fallback_model,
                env_key_names=("NVIDIA_API_KEY", "NIM_API_KEY", "NVIDIA_NIM_API_KEY", "nvidia_nim_api_key"),
                endpoint=NVIDIA_NIM_URL,
            )
            fallback_key = _first_env_value(env, spec.env_key_names)
            if not fallback_key:
                raise ValueError("Fallback requested but no NVIDIA/NIM API key was found")

            def fallback_extractor(image_path: Path, page_number: int, failure: dict) -> dict:
                result = _call_openai_compatible_vision(spec, fallback_key, image_path, page_number)
                result["fallback_parent_failure_type"] = failure.get("failure_type")
                result["fallback_parent_provider"] = failure.get("provider")
                result["fallback_parent_model"] = failure.get("model")
                return result

        if args.provider == "gemini":
            result = extract_pdf_with_gemini(
                pdf_path=args.pdf.resolve(),
                output_dir=args.out.resolve(),
                api_key=str(api_key),
                expected_questions=args.expected_questions,
                model_name=args.model,
                force=args.force,
                fallback_extractor=fallback_extractor,
            )
        else:
            spec = _primary_model_spec(args.provider, args.model)
            provider_key = _first_env_value(env, spec.env_key_names)
            if not provider_key:
                raise ValueError(f"No API key found for provider {args.provider}")
            page_delay = 5.0 if args.provider == "openrouter" else 0.0
            result = extract_pdf_with_openai_compatible_vision(
                pdf_path=args.pdf.resolve(),
                output_dir=args.out.resolve(),
                provider=spec.provider,
                model_name=spec.model,
                endpoint=spec.endpoint,
                api_key=provider_key,
                expected_questions=args.expected_questions,
                force=args.force,
                fallback_extractor=fallback_extractor,
                page_delay_seconds=page_delay,
            )
        print(f"questions={result.question_count}")
        print(f"qc_passed={result.qc_passed}")
        print(f"qc_status={result.qc_status}")
        print(f"merged={result.merged_path}")
        print(f"summary={result.summary_path}")
        return 0 if result.qc_passed else 1
    if args.command == "compare-models":
        report = compare_models(
            env_file=args.env_file.resolve(),
            reference_path=args.reference.resolve(),
            image_dir=args.image_dir.resolve(),
            output_dir=args.out.resolve(),
            pages=args.pages,
            force=args.force,
        )
        print(f"results={len(report['results'])}")
        print(f"report={args.out.resolve() / 'model_comparison_report.md'}")
        return 0
    if args.command == "investigate-extraction":
        report = build_extraction_investigation(args.batch_summary.resolve())
        out_path = args.out.resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        write_extraction_investigation_report(report, out_path)
        json_path = out_path.with_suffix(".json")
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"pdfs={report['pdf_count']}")
        print(f"report={out_path}")
        print(f"json={json_path}")
        return 0
    if args.command == "retry-failed-batch":
        env = _read_env(args.env_file.resolve())
        if args.provider == "gemini":
            primary_key = read_api_key(args.env_file.resolve())
            endpoint = None
        else:
            spec = _primary_model_spec(args.provider, args.model)
            primary_key = _first_env_value(env, spec.env_key_names)
            if not primary_key:
                raise ValueError(f"No API key found for provider {args.provider}")
            endpoint = spec.endpoint
        page_delay = 5.0 if args.provider == "openrouter" else 0.0
        report = retry_failed_extractions(
            batch_summary_path=args.batch_summary.resolve(),
            investigation_path=args.investigation.resolve() if args.investigation else None,
            output_root=args.out.resolve(),
            primary_provider=args.provider,
            primary_model=args.model,
            primary_endpoint=endpoint,
            primary_api_key=primary_key,
            force=args.force,
            page_delay_seconds=page_delay,
        )
        print(f"retried={len(report['rows'])}")
        print(f"summary={args.out.resolve() / 'batch_summary.md'}")
        return 0
    if args.command == "compare-phases":
        report = build_phase_comparison(
            {
                "P1": {
                    "summary_path": str(Path("extraction_batch/tier1_gemini/batch_summary.json").resolve()),
                    "default_provider_model_notes": "google_ai_studio / models/gemini-3.1-flash-lite; llm-only native phase",
                    "architecture_notes": "Original llm-only extraction phase using Gemini page-image extraction without deterministic answer evidence.",
                },
                "P2": {
                    "summary_path": str(Path("extraction_batch/tier1_gemini/precision_batch_summary.json").resolve()),
                    "default_provider_model_notes": "google_ai_studio / models/gemini-3.1-flash-lite; precision evidence layer",
                    "architecture_notes": "Precision pipeline added layout crops, HSV green-answer evidence, and canonical QC on top of Gemini extraction.",
                },
                "P2_patch1": {
                    "summary_path": str(Path("extraction_reruns/p2_all_pdfs_20260524/batch_summary.json").resolve()),
                    "structural_path": str(Path("reports/p2_failure_investigation_20260524.json").resolve()),
                    "default_provider_model_notes": "google_ai_studio / models/gemini-3.1-flash-lite; patched failure metadata",
                    "architecture_notes": "Patch1 added structural failure investigation and metadata after the all-PDF rerun exposed quota pages being merged as empty output.",
                },
                "P2_patch2": {
                    "summary_path": str(Path("extraction_reruns/p2_nim_primary_retry_20260524/batch_summary.json").resolve()),
                    "default_provider_model_notes": "nvidia_nim / mistralai/mistral-medium-3.5-128b; NIM-first retry batch",
                    "architecture_notes": "Patch2 retries failed PDFs with NIM as the primary carrier instead of Gemini-first, preserving the precision QC stack.",
                },
            }
        )
        write_phase_comparison(report, args.out_md.resolve(), args.out_json.resolve())
        print(f"report={args.out_md.resolve()}")
        return 0
    parser.error(f"Unknown command: {args.command}")
    return 2


def _primary_model_spec(provider: str, model: str) -> ModelSpec:
    if provider == "nvidia_nim":
        return ModelSpec(
            provider=provider,
            model=model,
            env_key_names=("NVIDIA_API_KEY", "NIM_API_KEY", "NVIDIA_NIM_API_KEY", "nvidia_nim_api_key"),
            endpoint=NVIDIA_NIM_URL,
        )
    return ModelSpec(
        provider=provider,
        model=model,
        env_key_names=("OPENROUTER_API_KEY", "OPENROUTER_KEY", "openrouter", "deep_seek_open_router"),
        endpoint="https://openrouter.ai/api/v1/chat/completions",
    )


if __name__ == "__main__":
    raise SystemExit(main())
