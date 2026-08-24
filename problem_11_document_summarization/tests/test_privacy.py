from pathlib import Path


def test_project_does_not_contain_email_storage_files():
    root = Path(__file__).parents[1]
    forbidden = {"emails.json", "emails.csv", "email.db", "email.sqlite"}
    assert not any(path.name in forbidden for path in root.rglob("*"))
