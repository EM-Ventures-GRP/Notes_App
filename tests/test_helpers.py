
import pytest
from app.notes_app import list_unique_categories, category_counts, category_note_lengths, category_word_counts

# --- Tests for list_unique_categories ---

def test_list_unique_categories_basic():
    notes = {
        "work": ["call client"],
        "groceries": ["milk"],
        "done": []
    }
    result = list_unique_categories(notes)
    assert result == {"work", "groceries", "done"}

def test_list_unique_categories_empty():
    notes = {}
    result = list_unique_categories(notes)
    assert result == set()

def test_list_unique_categories_case_sensitive():
    notes = {"Work": ["task"], "work": ["another"]}
    result = list_unique_categories(notes)
    # keys are kept exactly as they appear
    assert result == {"Work", "work"}

# --- Tests for category_counts ---

def test_category_counts_basic():
    notes = {
        "work": ["call client", "send email"],
        "groceries": ["milk"],
        "done": []
    }
    result = category_counts(notes)
    assert result == {"work": 2, "groceries": 1, "done": 0}

def test_category_counts_empty():
    notes = {}
    result = category_counts(notes)
    assert result == {}    

# --- Tests for Category_note_lengths ---

def test_category_note_lengths_basic():
    notes = {
        "work": ["call client", "send email"],
        "groceries": ["milk", "buy bread"]
    }
    result = category_note_lengths(notes)
    assert result == {"work": 21, "groceries": 13}


def test_category_note_lengths_empty_category():
    notes = {"work": []}
    result = category_note_lengths(notes)
    assert result == {"work": 0}


def test_category_note_lengths_empty_notes():
    notes = {}
    result = category_note_lengths(notes)
    assert result == {}

# --- Testo for Category_word_counts---

def test_category_word_counts_basic():
    notes = {
        "work": ["send urgent email", "call client"],
        "groceries": ["urgent: milk", "buy bread"],
    }
    result = category_word_counts(notes, "urgent")
    assert result == {"work": 1, "groceries": 1}

def test_category_word_counts_none_found():
    notes = {"work": ["call client"], "groceries": ["buy bread"]}
    result = category_word_counts(notes, "urgent")
    assert result == {"work": 0, "groceries": 0}

def test_category_word_counts_case_insensitive():
    notes = {"work": ["Urgent task", "not important"]}
    result = category_word_counts(notes, "urgent")
    assert result == {"work": 1}

