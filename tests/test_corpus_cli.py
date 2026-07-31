from __future__ import annotations

from pathlib import Path

from ssc_corpus.cli import main


def test_extract_pdf_missing_gemini_key_returns_clean_error(tmp_path: Path, capsys) -> None:
    pdf_path = tmp_path / "paper.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 sample")
    env_path = tmp_path / ".env"

    exit_code = main(
        [
            "extract-pdf",
            "--pdf",
            str(pdf_path),
            "--out",
            str(tmp_path / "out"),
            "--env-file",
            str(env_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error:" in captured.out
    assert "API key" in captured.out


def test_extract_pdf_missing_openrouter_key_returns_clean_error(tmp_path: Path, capsys) -> None:
    pdf_path = tmp_path / "paper.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 sample")
    env_path = tmp_path / ".env"

    exit_code = main(
        [
            "extract-pdf",
            "--provider",
            "openrouter",
            "--pdf",
            str(pdf_path),
            "--out",
            str(tmp_path / "out"),
            "--env-file",
            str(env_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error:" in captured.out
    assert "provider openrouter" in captured.out
