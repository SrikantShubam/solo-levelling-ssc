from pathlib import Path

import requests

from ssc_corpus.acquisition import _download


class _FakeResponse:
    def __init__(self, content: bytes, url: str, status_code: int, content_type: str) -> None:
        self.content = content
        self.url = url
        self.status_code = status_code
        self.headers = {"content-type": content_type}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


def test_download_http_uses_requests_and_persists_payload(monkeypatch, tmp_path: Path) -> None:
    def fake_get(url: str, timeout: int, headers: dict[str, str], verify: bool) -> _FakeResponse:
        assert "Mozilla" in headers["User-Agent"]
        assert verify is True
        return _FakeResponse(b"pdf-bytes", url, 200, "application/pdf")

    monkeypatch.setattr("ssc_corpus.acquisition.requests.get", fake_get)

    metadata = _download("https://example.com/file.pdf", tmp_path / "file.pdf")

    assert (tmp_path / "file.pdf").read_bytes() == b"pdf-bytes"
    assert metadata["http_status"] == "200"
    assert metadata["content_type"] == "application/pdf"


def test_download_ssc_legacy_host_disables_tls_verification(
    monkeypatch, tmp_path: Path
) -> None:
    def fake_get(url: str, timeout: int, headers: dict[str, str], verify: bool) -> _FakeResponse:
        assert verify is False
        return _FakeResponse(b"pdf-bytes", url, 200, "application/pdf")

    monkeypatch.setattr("ssc_corpus.acquisition.requests.get", fake_get)

    metadata = _download(
        "https://ssc.nic.in/SSCFileServer/PortalManagement/UploadedFiles/sample.pdf",
        tmp_path / "file.pdf",
    )

    assert (tmp_path / "file.pdf").read_bytes() == b"pdf-bytes"
    assert metadata["http_status"] == "200"
