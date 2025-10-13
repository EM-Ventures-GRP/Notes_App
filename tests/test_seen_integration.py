# tests/test_seen_integration.py
from app.notes_app import build_seen

def test_build_seen_uses_normalize():
    notes = {"General": ["To-do", "TO   DO!!"], "Work": [" to do  "]}
    s = build_seen(notes)
    assert s == {"to do"}
