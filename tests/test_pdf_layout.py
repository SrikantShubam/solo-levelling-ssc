from __future__ import annotations

from types import SimpleNamespace

from ssc_corpus.pdf_layout import inspect_pdf_layout


def test_inspect_pdf_layout_closes_document(monkeypatch, tmp_path) -> None:
    closed = {"value": False}

    class FakePage:
        rect = SimpleNamespace(x0=0.0, y0=0.0, x1=100.0, y1=100.0)

        def get_text(self, _mode: str):
            return []

    class FakeDoc:
        def __iter__(self):
            return iter([FakePage()])

        def close(self) -> None:
            closed["value"] = True

    monkeypatch.setitem(
        __import__("sys").modules,
        "fitz",
        SimpleNamespace(open=lambda _path: FakeDoc()),
    )

    layouts = inspect_pdf_layout(tmp_path / "paper.pdf")

    assert len(layouts) == 1
    assert closed["value"] is True
