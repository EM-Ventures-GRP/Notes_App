# Notes App v2.15 — CLI Notebook Organizer

A lightweight, command-line notes manager built in Python.  
It supports categories, editing, safe error handling, search, and persistent storage in a JSON file (`notes.json`).  
Designed as a learning project, the app demonstrates functions, dictionaries, nested loops, sets, error handling, and string handling while growing version-by-version with new features.  

## Features (v2.15)

- Add notes (with category, defaults to `"General"`)  
- Show notes grouped by category (with consistent numbering via `show_numbered()`)  
- Search notes (case-insensitive, highlights matches with `[ ]`)  
- Delete notes (safe error handling for invalid inputs)  
- Move notes between categories (auto-creates destination if missing)  
- **Edit notes** with duplicate guard + safe cancel  
- Case-insensitive duplicate detection using a `seen` set  
- Persistent save/load with JSON, including migration from older flat-list format  
- Friendly error messages and tidy UX  

##  How to Run

1. Clone this repo and navigate to the folder.  
2. Run the program with:  
   ```bash
   python3 notes_app.py

## Changelog
- v1.0: Basic Notes App (add, show, exit)
- v2.0: Persistent notes with file saving + search
- v2.1: Smarter logic — empty input guard, case-insensitive search with “no matches”, delete with confirmation
- v2.2: Added categories (optional `category|note` format), blocked duplicate note text across categories, and updated Show/Search to display `[category] note`.
- v2.3: Refactored menu features into functions (add, show, search, delete) for clarity and reuse.
- v2.4: Early practice with dictionaries (shaping {category: [notes...]} structure).
- v2.5: Added error handling with try/except, plus helper functions load_notes and save_notes for persistence.
- v2.6: Refactored app to use categories as dict keys, with nested loop for grouped display.
- v2.7: Introduced search across categories (case-insensitive), plus show_menu() helper for DRY code.
- v2.8: Added case-insensitive sorting for categories and notes, built move_note feature, and enhanced search with regex highlighting for matches.
- v2.9: Added small UX improvements using boolean logic (e.g., cleaner menu choice handling) and polished duplicate/error messages.
- v2.10: Added duplicate protection (case/space-insensitive) with normalize + find_note; blocks duplicates across all categories.
- v2.11: Added category maintenance tools — rename_category, merge_categories, and show_stats (dict comprehension).
- v2.12: Normalized categories with .lower() to make them case-insensitive; polished stats output with sorted keys.
- v2.13: Introduced seen set for fast duplicate detection (O(1) lookups). Kept seen synchronized on add/delete/load.
- v2.14: UX polish — improved duplicate handling flow, clearer error messages, and small code refactors for consistency.
- v2.15: New edit_note with seen-sync, show_numbered helper, robust load_notes with migration.


