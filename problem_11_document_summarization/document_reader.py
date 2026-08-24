"""Read TXT and DOCX email documents in memory without modifying them."""

from pathlib import Path


class DocumentReadError(Exception):
    """Safe error for document-reading problems."""


def extract_email_text(file_name: str) -> str:
    """Extract text from a supported document and return it in memory."""
    path = Path(file_name).expanduser()
    if not path.is_file():
        raise DocumentReadError("The document was not found.")
    if path.suffix.lower() == ".txt":
        text = path.read_text(encoding="utf-8-sig")
    elif path.suffix.lower() == ".docx":
        from docx import Document
        text = "\n".join(paragraph.text for paragraph in Document(path).paragraphs)
    else:
        raise DocumentReadError("Unsupported format. Use .txt or .docx.")
    if not text.strip():
        raise DocumentReadError("The document is empty.")
    return text.strip()
