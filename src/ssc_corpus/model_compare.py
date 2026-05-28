from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .extraction import _page_prompt, _strip_json_fences


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
NVIDIA_NIM_URL = "https://integrate.api.nvidia.com/v1/chat/completions"


@dataclass(frozen=True)
class ModelSpec:
    provider: str
    model: str
    env_key_names: tuple[str, ...]
    endpoint: str
    vision_capable: bool = True


DEFAULT_MODEL_SPECS = [
    ModelSpec(
        provider="openrouter",
        model="deepseek/deepseek-v4-flash:free",
        env_key_names=("OPENROUTER_API_KEY", "OPENROUTER_KEY", "openrouter"),
        endpoint=OPENROUTER_URL,
        vision_capable=False,
    ),
    ModelSpec(
        provider="nvidia_nim",
        model="google/gemma-3n-e2b-it",
        env_key_names=("NVIDIA_API_KEY", "NIM_API_KEY", "NVIDIA_NIM_API_KEY", "nvidia_nim_api_key"),
        endpoint=NVIDIA_NIM_URL,
    ),
    ModelSpec(
        provider="nvidia_nim",
        model="google/gemma-3n-e4b-it",
        env_key_names=("NVIDIA_API_KEY", "NIM_API_KEY", "NVIDIA_NIM_API_KEY", "nvidia_nim_api_key"),
        endpoint=NVIDIA_NIM_URL,
    ),
    ModelSpec(
        provider="nvidia_nim",
        model="microsoft/phi-4-multimodal-instruct",
        env_key_names=("NVIDIA_API_KEY", "NIM_API_KEY", "NVIDIA_NIM_API_KEY", "nvidia_nim_api_key"),
        endpoint=NVIDIA_NIM_URL,
    ),
    ModelSpec(
        provider="nvidia_nim",
        model="meta/llama-3.2-11b-vision-instruct",
        env_key_names=("NVIDIA_API_KEY", "NIM_API_KEY", "NVIDIA_NIM_API_KEY", "nvidia_nim_api_key"),
        endpoint=NVIDIA_NIM_URL,
    ),
    ModelSpec(
        provider="nvidia_nim",
        model="nvidia/llama-3.1-nemotron-nano-vl-8b-v1",
        env_key_names=("NVIDIA_API_KEY", "NIM_API_KEY", "NVIDIA_NIM_API_KEY", "nvidia_nim_api_key"),
        endpoint=NVIDIA_NIM_URL,
    ),
    ModelSpec(
        provider="nvidia_nim",
        model="google/deplot",
        env_key_names=("NVIDIA_API_KEY", "NIM_API_KEY", "NVIDIA_NIM_API_KEY", "nvidia_nim_api_key"),
        endpoint=NVIDIA_NIM_URL,
    ),
]


def compare_models(
    env_file: Path,
    reference_path: Path,
    image_dir: Path,
    output_dir: Path,
    pages: list[int],
    model_specs: list[ModelSpec] | None = None,
    force: bool = False,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    env = _read_env(env_file)
    specs = model_specs or DEFAULT_MODEL_SPECS
    reference = json.loads(reference_path.read_text(encoding="utf-8"))
    reference_by_page = _reference_by_page(reference)
    results = []

    for spec in specs:
        model_dir = output_dir / _safe_name(f"{spec.provider}_{spec.model}")
        model_dir.mkdir(parents=True, exist_ok=True)
        api_key = _first_env_value(env, spec.env_key_names)
        if not spec.vision_capable:
            results.append(
                {
                    "provider": spec.provider,
                    "model": spec.model,
                    "status": "SKIPPED",
                    "reason": "model_marked_text_only_not_valid_for_page_image_ocr",
                }
            )
            continue
        if not api_key:
            results.append(
                {
                    "provider": spec.provider,
                    "model": spec.model,
                    "status": "SKIPPED",
                    "reason": f"missing_key_any_of_{','.join(spec.env_key_names)}",
                }
            )
            continue

        page_scores = []
        for page in pages:
            image_path = image_dir / f"page_{page:02d}.png"
            raw_path = model_dir / f"page_{page:02d}.json"
            if raw_path.exists() and not force:
                page_result = json.loads(raw_path.read_text(encoding="utf-8"))
            else:
                page_result = _call_openai_compatible_vision(spec, api_key, image_path, page)
                raw_path.write_text(json.dumps(page_result, ensure_ascii=False, indent=2), encoding="utf-8")
            score = score_page_result(page_result, reference_by_page.get(page, []), page)
            page_scores.append(score)
        results.append(_summarize_model(spec, page_scores))

    report = {"pages": pages, "results": results}
    (output_dir / "model_comparison_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _write_markdown_report(report, output_dir / "model_comparison_report.md")
    return report


def score_page_result(result: dict[str, Any], reference_questions: list[dict[str, Any]], page: int) -> dict[str, Any]:
    questions = result.get("questions") or []
    count_match = len(questions) == len(reference_questions)
    comparable = zip(questions, reference_questions)
    correct_matches = 0
    chosen_matches = 0
    chosen_reference_count = 0
    fills_reference_missing_chosen = 0
    option_shape_matches = 0
    text_scores = []
    issues = []
    for idx, (candidate, reference) in enumerate(comparable, start=1):
        if str(candidate.get("correct_option_label")) == str(reference.get("correct_option_label")):
            correct_matches += 1
        else:
            issues.append(f"q{idx}_correct_mismatch")
        if reference.get("chosen_option_label") is not None:
            chosen_reference_count += 1
            if str(candidate.get("chosen_option_label")) == str(reference.get("chosen_option_label")):
                chosen_matches += 1
            else:
                issues.append(f"q{idx}_chosen_mismatch")
        elif candidate.get("chosen_option_label") is not None:
            fills_reference_missing_chosen += 1
        candidate_labels = [str(item.get("label")) for item in candidate.get("options", []) if isinstance(item, dict)]
        if candidate_labels == ["1", "2", "3", "4"]:
            option_shape_matches += 1
        else:
            issues.append(f"q{idx}_option_shape_bad")
        text_scores.append(
            SequenceMatcher(
                None,
                " ".join(str(candidate.get("question_text_full", "")).split()).lower(),
                " ".join(str(reference.get("question_text_full", "")).split()).lower(),
            ).ratio()
        )
    denom = max(len(reference_questions), 1)
    return {
        "page": page,
        "status": "PASS" if count_match and not issues else "FAIL",
        "question_count": len(questions),
        "reference_question_count": len(reference_questions),
        "count_match": count_match,
        "correct_accuracy": correct_matches / denom,
        "chosen_accuracy": chosen_matches / max(chosen_reference_count, 1),
        "chosen_reference_count": chosen_reference_count,
        "fills_reference_missing_chosen": fills_reference_missing_chosen,
        "option_shape_accuracy": option_shape_matches / denom,
        "mean_text_similarity": sum(text_scores) / len(text_scores) if text_scores else 0,
        "issues": issues,
    }


def _call_openai_compatible_vision(
    spec: ModelSpec, api_key: str, image_path: Path, page: int
) -> dict[str, Any]:
    payload = {
        "model": spec.model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _page_prompt(page)},
                    {
                        "type": "image_url",
                        "image_url": {"url": _image_data_url(image_path)},
                    },
                ],
            }
        ],
        "temperature": 0,
    }
    request = Request(
        spec.endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://local.ssc-corpus",
            "X-Title": "ssc-corpus-model-comparison",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=180) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {
            "page": page,
            "questions": [],
            "warnings": [f"ERROR HTTP {exc.code}: {body[:1000]}"],
            "page_status": "ERROR",
            "provider": spec.provider,
            "model": spec.model,
        }
    except URLError as exc:
        return {
            "page": page,
            "questions": [],
            "warnings": [f"ERROR URL: {exc}"],
            "page_status": "ERROR",
            "provider": spec.provider,
            "model": spec.model,
        }
    except TimeoutError as exc:
        return {
            "page": page,
            "questions": [],
            "warnings": [f"ERROR TimeoutError: {exc}"],
            "page_status": "ERROR",
            "provider": spec.provider,
            "model": spec.model,
        }

    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    if isinstance(content, list):
        content = "\n".join(str(item.get("text", item)) for item in content)
    text = _strip_json_fences(str(content))
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        return {
            "page": page,
            "questions": [],
            "warnings": [f"ERROR JSONDecodeError: {exc}", text[:2000]],
            "page_status": "ERROR",
            "provider": spec.provider,
            "model": spec.model,
        }
    if not isinstance(parsed, dict):
        return {
            "page": page,
            "questions": [],
            "warnings": [f"ERROR Schema: expected object got {type(parsed).__name__}", text[:2000]],
            "page_status": "ERROR",
            "provider": spec.provider,
            "model": spec.model,
        }
    parsed["page"] = page
    parsed.setdefault("questions", [])
    parsed.setdefault("warnings", [])
    parsed.setdefault("page_status", "OK")
    parsed.setdefault("failure_type", None)
    parsed.setdefault("provider", spec.provider)
    parsed.setdefault("model", spec.model)
    parsed.setdefault("usage", data.get("usage"))
    return parsed


def _reference_by_page(reference: dict[str, Any]) -> dict[int, list[dict[str, Any]]]:
    pages: dict[int, list[dict[str, Any]]] = {}
    for question in reference.get("questions", []):
        page = int(question["source_page"])
        pages.setdefault(page, []).append(question)
    return pages


def _summarize_model(spec: ModelSpec, page_scores: list[dict[str, Any]]) -> dict[str, Any]:
    if not page_scores:
        return {"provider": spec.provider, "model": spec.model, "status": "NO_PAGES"}
    return {
        "provider": spec.provider,
        "model": spec.model,
        "status": "PASS" if all(score["status"] == "PASS" for score in page_scores) else "FAIL",
        "pages": page_scores,
        "mean_correct_accuracy": _mean(page_scores, "correct_accuracy"),
        "mean_chosen_accuracy": _mean(page_scores, "chosen_accuracy"),
        "fills_reference_missing_chosen": sum(
            int(score.get("fills_reference_missing_chosen", 0)) for score in page_scores
        ),
        "mean_option_shape_accuracy": _mean(page_scores, "option_shape_accuracy"),
        "mean_text_similarity": _mean(page_scores, "mean_text_similarity"),
    }


def _write_markdown_report(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Model Comparison Report",
        "",
        f"- Pages tested: {report['pages']}",
        "",
        "| Provider | Model | Status | Correct Acc | Chosen Acc | Fills Missing Chosen | Option Shape | Text Similarity | Reason |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["results"]:
        lines.append(
            "| {provider} | {model} | {status} | {correct:.2f} | {chosen:.2f} | {fills} | {options:.2f} | {text:.2f} | {reason} |".format(
                provider=row["provider"],
                model=row["model"],
                status=row["status"],
                correct=row.get("mean_correct_accuracy", 0),
                chosen=row.get("mean_chosen_accuracy", 0),
                fills=row.get("fills_reference_missing_chosen", 0),
                options=row.get("mean_option_shape_accuracy", 0),
                text=row.get("mean_text_similarity", 0),
                reason=row.get("reason", ""),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _image_data_url(image_path: Path) -> str:
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _read_env(path: Path) -> dict[str, str]:
    env = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = re.match(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*[\"']?([^\"'\r\n]+)", line)
        if match:
            env[match.group(1)] = match.group(2).strip()
    return env


def _first_env_value(env: dict[str, str], names: tuple[str, ...]) -> str | None:
    for name in names:
        if env.get(name):
            return env[name]
    return None


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def _mean(rows: list[dict[str, Any]], key: str) -> float:
    return sum(float(row.get(key, 0)) for row in rows) / len(rows)
