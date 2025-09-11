# Notes App  

A lightweight, command-line notes manager built in Python.  
It supports categories, safe error handling, search with highlighting, and persistent storage in a JSON file (`notes.json`).  
Designed as a learning project, the app demonstrates functions, dictionaries, nested loops, error handling, sorting, and string handling while growing version-by-version with new features.  

---

## Features
- Add notes (with category, defaults to `"General"`)  
- Show notes grouped by category (case-insensitive sorting of categories and notes)  
- Delete notes (safe error handling: `ValueError`, `KeyError`, `IndexError`)  
- Search notes (case-insensitive, highlights matches with `[ ]`)  
- Move notes between categories (auto-creates destination if missing)  
- Persistent save/load with JSON, including migration from older flat-list format  
- Friendly error messages and tidy UX  

---

## How to Run
1. Clone this repo and navigate to the folder.  
2. Run the program with:  
   ```bash
   python notes_app.py


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


