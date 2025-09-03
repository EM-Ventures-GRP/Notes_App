# Notes App

A lightweight, command-line notes manager built in Python.  
It supports optional categories, duplicate protection, and persistent storage in a text file (`notes.txt`).  
Designed as a learning project, the app demonstrates file I/O, conditionals, loops, and string handling while growing version-by-version with new features.



## Features
- Add notes (with empty input guard)
- Optional categories: add notes in the format `category|note`
- Duplicate protection: blocks duplicate note text (case-insensitive, even across categories)
- Show all notes (with numbering and `[category]` display if present)
- Search notes (case-insensitive, matches in category or text, pretty display)
- Delete notes (with confirmation + file rewrite)
- Invalid menu choice handling
- Data persists between runs using `notes.txt`


## How to Run
1. Open a terminal and navigate to the `notes_app` folder.  
2. Run the program with:  
   ```bash
   python app.py

## Changelog
- v1.0: Basic Notes App (add, show, exit)
- v2.0: Persistent notes with file saving + search
- v2.1: Smarter logic — empty input guard, case-insensitive search with “no matches”, delete with confirmation
- v2.2: Added categories (optional `category|note` format), blocked duplicate note text across categories, and updated Show/Search to display `[category] note`.

