
from __future__ import annotations
import json, os
from app.utils import load_notes_safe

def write(fp, content: str):
    fp.write_text(content, encoding="utf-8")

def test_load_valid_file(tmp_path):
    p = tmp_path / "notes.json"
    data = {"General": ["buy milk"], "Work": ["send email"]}
    p.write_text(json.dumps(data), encoding="utf-8")
    notes = load_notes_safe(str(p))
    assert notes == data

def test_missing_file_returns_empty(tmp_path):
    p = tmp_path / "notes.json"
    notes = load_notes_safe(str(p))
    assert notes == {}

def test_corrupt_file_is_backed_up_and_returns_empty(tmp_path):
    p = tmp_path / "notes.json"
    write(p, "{bad json")
    notes = load_notes_safe(str(p))
    assert notes == {}
    # backup exists (could be ..._corrupt.json or ..._corrupt_2.json etc.)
    backups = list(tmp_path.glob("notes_corrupt*.json"))
    assert len(backups) == 1

def test_wrong_type_returns_empty_without_backup(tmp_path):
    p = tmp_path / "notes.json"
    p.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")
    notes = load_notes_safe(str(p))
    assert notes == {}
    # No corrupt backup should be created for valid JSON wrong type
    backups = list(tmp_path.glob("notes_corrupt*.json"))
    assert backups == []

