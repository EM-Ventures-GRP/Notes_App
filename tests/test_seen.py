import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from notes_app import build_seen

def test_build_seen_basic():
    notes = {"home": ["buy milk"], "work": ["send invoice"]}
    assert build_seen(notes) == {"buy milk", "send invoice"}

def test_build_seen_empty():
    assert build_seen({}) == set()
