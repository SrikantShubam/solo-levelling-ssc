from pathlib import Path

from ssc_corpus.cli import main


def test_init_creates_expected_structure(tmp_path: Path) -> None:
    exit_code = main(["init", "--root", str(tmp_path)])

    assert exit_code == 0
    assert (tmp_path / "raw_sources" / "primary").is_dir()
    assert (tmp_path / "raw_sources" / "derived_reference").is_dir()
    assert (tmp_path / "manifests" / "download_manifest.csv").is_file()
    assert (tmp_path / "manifests" / "integrity_report.csv").is_file()
    assert (tmp_path / "reports").is_dir()
    assert (tmp_path / "templates" / "acquisition_seed.csv").is_file()
