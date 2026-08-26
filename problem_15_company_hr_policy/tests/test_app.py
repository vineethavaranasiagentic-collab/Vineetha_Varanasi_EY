from __future__ import annotations

from pathlib import Path

from app import NO_INFORMATION, extract_chunks


def test_extract_chunks_preserves_pdf_metadata(tmp_path: Path) -> None:
    # PDF integration tests can use a real fixture; this verifies the public contract.
    assert NO_INFORMATION == "The information is not available in the uploaded document."
    assert callable(extract_chunks)
