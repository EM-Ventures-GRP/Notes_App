from __future__ import annotations
import re
import os
from datetime import datetime
import json, shutil, os
from typing import Dict, List


# Debug toggle (one switch)
# prefer env var if present; else default False.
DEBUG = os.getenv("NOTES_DEBUG", 0) in ("1", "true", "True")

def trace(msg: str):
    """Tiny debug helper that shows timestamp + message, only when it's ON"""  
    if not DEBUG:
        return
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}]{msg}")



def normalize(s: str) -> str:
    """Normalize a note for dedup checks:
    - trim outer whitespace
    - collapse inner spaces
    - lowercase
    - replace punctuation with spaces
    """
    trace(f"[enter normalize] {s!r}")
    s = s.strip()
    s = " ".join(s.split())
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)   # <-- replace non-alphanum with ONE space
    s = " ".join(s.split())              # <-- collapse multiple spaces to one
    trace(f"[exit  normalize],{s!r}")
    return s
#--------------------------------------------------------------------------------

NotesDict = Dict[str, List[str]]

def load_notes_safe(path: str = "notes.json") -> NotesDict:
    """
    Safely load notes JSON, guarding against missing/corrupt/wrong-type files.
    Returns {} on any recoverable problem. Never raises for common I/O/JSON issues.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[WARN] {path} not found. Starting fresh.")
        trace("Returning empty notes due to missing file.")
        return {}
    except json.JSONDecodeError:
        print(f"[ERROR] {path} is corrupt. Backing it up and starting fresh.")
        try:
            backup = path.replace(".json", "_corrupt.json")
            # If a previous corrupt backup exists, keep the newest by appending a counter
            if os.path.exists(backup):
                i = 2
                while os.path.exists(path.replace(".json", f"_corrupt_{i}.json")):
                    i += 1
                backup = path.replace(".json", f"_corrupt_{i}.json")
            shutil.move(path, backup)
            trace(f"Moved corrupt file to {backup}")
        except Exception as e:
            print(f"[WARN] Could not back up corrupt file: {e}")
        return {}
    except Exception as e:
        print(f"[ERROR] Unexpected load issue: {e}")
        return {}

    if not isinstance(data, dict):
        print(f"[WARN] {path} contained JSON but not a dict. Resetting to empty.")
        trace(f"Type was {type(data).__name__}; expected dict[str, list[str]].")
        return {}

    # Optional: enforce values are lists of strings to be extra safe
    clean: NotesDict = {}
    for cat, items in data.items():
        if isinstance(cat, str) and isinstance(items, list):
            clean_items = [str(x) for x in items]
            clean[cat] = clean_items
        else:
            print(f"[WARN] Dropping malformed entry for category {cat!r}.")
    trace(f"Loaded {len(clean)} categories from {path}.")
    return clean


