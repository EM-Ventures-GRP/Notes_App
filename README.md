# 🗒️ Notes App v2.18 — CLI Notebook Organizer

A lightweight, command-line notes manager built in Python.  
It supports categories, editing, safe error handling, search, and persistent storage in a JSON file (`notes.json`).  
Designed as a learning project, the app demonstrates **functions, dictionaries, nested loops, sets, comprehensions, error handling, and string normalization** while growing version-by-version with new features.

---

##  Features (v2.18)

- **Add notes** with optional category (defaults to `"general"`).  
- **Show notes** grouped by category with consistent numbering via `show_numbered()`.  
- **Search notes** (case-insensitive, highlights matches with `[ ]`).  
- **Delete notes** with confirmation; handles invalid inputs safely; auto-removes empty categories; keeps `seen` synchronized.  
- **Move notes** between categories (auto-creates destination if missing, includes no-op guard, and requires confirmation).  
- **Edit notes** with duplicate guard, safe cancel, and confirmation flow.  
- **Duplicate detection** via a `seen` set (case/space-insensitive).  
- **Persistent save/load** with JSON, including migration from older flat-list format.  
- **Guarded loader (`load_notes_safe`)** for corruption tolerance and data recovery.  
- **Friendly error messages** and tidy CLI UX.  
- **Unit-tested helpers** (`list_unique_categories`, etc.) using `pytest` for safer refactors and regression protection.

---

##  Architecture Highlights

- `app/notes_app.py` — main CLI loop and menu actions  
- `app/utils.py` — helpers (`load_notes_safe`, `save_notes`, `normalize`, `trace`)  
- `tests/` — pytest coverage for helpers and edge cases  

---


## Next Milestone: v2.19

- Add type hints (`NotesDict`, `Optional[str]`)  
- Strengthen `load_notes_safe()` with empty-file detection  
- Enforce consistent typing via VS Code + Pylance  
- Add `pytest` for empty/corrupt file edge cases

## How to Run

1. Clone this repo and navigate to the folder.  
2. Run the program with:  
   ```bash
   python3 notes_app.py


## Changelog

- **v1.0**: Basic Notes App (add, show, exit).
- **v2.0**: Persistent notes with file saving + search.
- **v2.1**: Smarter logic — empty input guard, case-insensitive search with “no matches”, delete with confirmation.
- **v2.2**: Added categories (optional `category|note` format); blocked duplicate note text across categories; updated Show/Search to display `[category] note`.
- **v2.3**: Refactored menu features into functions (add, show, search, delete) for clarity and reuse.
- **v2.4**: Early practice with dictionaries (introduced `{category: [notes...]}` structure).
- **v2.5**: Added error handling (`try/except`) + helper functions `load_notes()` and `save_notes()` for persistence.
- **v2.6**: Refactored app to use categories as dict keys with nested loop for grouped display.
- **v2.7**: Introduced search across categories (case-insensitive) + `show_menu()` helper for DRY code.
- **v2.8**: Added case-insensitive sorting for categories and notes; built `move_note()` feature; enhanced search with regex highlighting.
- **v2.9**: UX polish using boolean logic (cleaner menu choice handling + duplicate/error messages).
- **v2.10**: Added duplicate protection (case/space-insensitive) using `normalize()` + `find_note()`; blocks duplicates globally.
- **v2.11**: Added category maintenance tools (`rename_category`, `merge_categories`, `show_stats`) using dict comprehensions.
- **v2.12**: Normalized categories with `.lower()` for consistency; improved `show_stats()` output with sorted keys.
- **v2.13**: Introduced `seen` set for fast duplicate detection (O(1) lookups). Kept `seen` synced on add/delete/load.
- **v2.14**: UX polish — improved duplicate-handling flow, clearer error messages, and small code refactors.
- **v2.15**: New `edit_note()` with seen-sync, `show_numbered()` helper, and robust `load_notes()` with migration support.
- **v2.16**: Integrated `confirm()` helper across edit, move, and delete — explicit `"y"` confirmation required before mutating.
- **v2.17**: Added no-op guards to prevent unnecessary actions (e.g., moving to same category or editing identical text).
- **v2.18**: Introduced `load_notes_safe()` with corruption tolerance + pytest coverage; added foundational helpers (`safe_int`, `normalize_category`) for from-scratch muscle building.


