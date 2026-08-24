from pathlib import Path

import pytest

from document_reader import DocumentReadError, extract_email_text


def test_txt_is_read_without_modification(tmp_path: Path):
    source = tmp_path / "email.txt"
    source.write_text("Subject: Help\nPlease help.", encoding="utf-8")
    assert extract_email_text(str(source)) == "Subject: Help\nPlease help."


def test_missing_document_is_rejected(tmp_path: Path):
    with pytest.raises(DocumentReadError):
        extract_email_text(str(tmp_path / "missing.txt"))


def test_unsupported_document_is_rejected(tmp_path: Path):
    source = tmp_path / "email.pdf"
    source.write_text("content", encoding="utf-8")
    with pytest.raises(DocumentReadError):
        extract_email_text(str(source))
