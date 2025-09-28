
# -*- coding: utf-8 -*-
"""Notes_App V2.15.ipynb"""

from os import remove
import json
from typing import Dict, List
import re

NotesDict = Dict[str, List[str]]

# ------------------------------
# Helpers
# ------------------------------
def show_menu():
    print("""
1. Add note
2. Show notes
3. Delete note
4. Search notes
5. Move note
6. List categories
7. Rename categories
8. Merge categories
9. Stats
10. Edit note
11. Save & Exit
""")
#----------------------------------------------------------

def load_notes(path: str = "notes.json") -> tuple[NotesDict, set[str]]:
    """
    Return notes as {category: [notes...]}.
    Handle:
      - Missing file
      - Corrupt JSON
      - Migration from old list -> {"General": [...]}
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        notes: NotesDict = {}
        seen: set[str] = set()
        return notes, seen
    except json.JSONDecodeError:
        print("Warning: notes file corrupted or empty. Starting fresh.")
        notes: NotesDict = {}
        return notes, build_seen(notes)
# Optional: if someday you save {"notes": {...}, "seen": []}, support it here.
    if isinstance(data, dict) and "notes" in data:
        raw_notes = data.get("notes", {})
        raw_seen = data.get("seen", [])
        notes ={}
        for k, v in raw_notes.items():
            key = str(k).strip().lower()
            if isinstance(v, list):
              notes[key] = [str(x) for x in v]
            else:
              notes[key] = [str(v)]

    # seen comes from file but we still constrain it to only notes that exist
        file_seen = {str(x) for x in raw_seen}
        computed_seen = build_seen(notes)
        seen = file_seen & computed_seen if file_seen else computed_seen
        return notes, seen

    # Legacy schemas:
    if isinstance(data, list):
        # old flat list -> single "general" bucket
        notes = {"general": [str(x) for x in data]}
    elif isinstance(data, dict):
        notes = {}
        for k, v in data.items():
            key = str(k).strip().lower()
            if isinstance(v, list):
                notes[key] = [str(x) for x in v]
            else:
                notes[key] = [str(v)]
    else:
        notes = {}

    return notes, build_seen(notes)
#----------------------------------------------------------------------------------
def save_notes(notes: NotesDict, path: str = "notes.json") -> None:
    """Save notes as JSON"""
    # Ensure valid dict-of-lists
    to_write = {}
    for k, v in notes.items():
        if isinstance(v, list):
            to_write[str(k)] = [str(x) for x in v]
        else:
            to_write[str(k)] = [str(v)]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(to_write, f, indent=2, ensure_ascii=False)
#----------------------------------------------------------------------------------
def normalize(s: str) -> str:
    """Trim, collapse internal spaces, lowercase — for fair comparisons."""
    return " ".join(s.strip().split()).lower()
#---------------------------------------------------------------------------------
def find_note(notes: NotesDict, text: str):
    """
    If a normalized duplicate exists anywhere, return (category, one_based_index).
    Otherwise return None.
    """
    target = normalize(text)
    for cat, items in notes.items():
        for i, n in enumerate(items, 1):
            if normalize(n) == target:
                return (cat, i)
    return None
#--------------------------------------------------------------------------------
def add_note(notes: NotesDict, text: str, category: str, seen: set[str]) -> None:
    category = (category or "General").strip().lower()
    text = text.strip()
    if not text:
        print("Empty note, cancelled.")
        return

    norm = text.lower()
    if norm in seen:
        print("Duplicate note. Not added!")
        return


        # if no duplicate, add as usual
    notes.setdefault(category, []).append(text)
    seen.add(norm)
    print(f"Note added to {category}.")
#-----------------------------------------------------------------------
def show_notes_grouped(notes: NotesDict) -> None:
    """Show notes grouped by category."""
    if not notes:
        print("(no notes yet)")
        return
    for cat, items in notes.items():
        print(f"\n{cat.upper()}:")
        show_numbered(items)
#---------------------------------------------------------------------------
def delete_note(notes: NotesDict, category: str, idx_one_based: int, seen: set[str]) -> str | None:

    try:
        idx = idx_one_based - 1
        cat_list = notes[category]
        note_to_remove = cat_list[idx]
    except KeyError:
        print("no such category")
        return None
    except IndexError:
        print("That number doesn't exist")
        return None
    
# Shows what will be deleted
    print(f"About to delete: '{note_to_remove}' from '{category}':")
    if not confirm("Are you sure you want to delete this note? (y/n):"):
       print("Canceled!")
       return None
    
#Safe to delete now
    removed = cat_list.pop(idx)

# IF category is now empty, remove category
    
    if not cat_list:
        del notes[category]

#Sync the seen set (only discard if that text no longer exists anywhere) 

    norm = removed.lower()      
    still_exists = any(norm in[n.strip().lower()for n in items] for items in notes.values())

    if not still_exists:
        seen.discard(norm)

    return removed

#------------------------------------------------------------------------------
def search_notes(notes: NotesDict, term: str) -> None:
    term = term.strip()
    if not term:
        print("Empty search.")
        return

    # Compile regex for case-insensitive search
    pattern = re.compile(re.escape(term), re.IGNORECASE)
    found = False

    for cat, items in notes.items():            # outer loop
        for i, note in enumerate(items, 1):     # inner loop
            if pattern.search(note):
               highlighted = pattern.sub(lambda m:f"[{m.group(0)}]", note)
               print(f"found in {cat}: {i}. {highlighted}")
               found = True

    if not found:
        print("No results.")
#---------------------------------------------------------------------------------
def move_note(notes: NotesDict, seen: set[str]) -> str | None:
    """
   Move a single note from one category to another, with preview + confirmation.

    Args:
        notes: Mapping of category -> list of notes (both treated case-insensitively).
        seen:  Global set of lowercase note texts used to enforce case-insensitive uniqueness.

    Returns:
        The moved note's exact text on success; None on cancel or when no change is performed.

    Edge cases handled:
        - Missing or empty source category (no move).
        - Index out of range (no move).
        - Destination auto-created if it doesn't exist.
        - Moving to the same category is a no-op (guard).
        - Duplicate (case-insensitive) already in destination → block move (no data loss).
    """
    src = input("From which category?").strip().lower()
    if src not in notes or not notes[src]:
        print(f"No notes in '{src}' (or category mising).")
        return None

    print(f"\nNotes in '{src}'") 
    show_numbered(notes[src])

    try:
        idx_raw = input("Which note # to move?").strip()
        idx = int(idx_raw) -1
        note_text = notes[src][idx]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None
  
    dest = input("To which category?").strip().lower()
    if dest == src:
        print("Note is alredy in that category!")
        return None
    
# Prevents duplicates in destination
    dest_list = notes.setdefault(dest,[])    
    if any(n.lower() == note_text.lower() for n in dest_list): # Blocks any dupplicates
        print("A note with the same text already exists! Note blocked.")
        return None

    print("\nPreview:")
    print(f"  Move: {note_text!r}")
    print(f"  From: '{src}' to: '{dest}'")
    if not confirm("Proceed with move? (y/n) "):
        print("Cancelled!")
        return None

# Perform mutation after confirmation only
    removed = notes[src].pop(idx)
    dest_list.append(removed)

#Optional: clean up empty source category
    return removed

#--------------------------------------------------------------------------------
def list_categories(notes: NotesDict) -> None:
    if not notes:
        print("(no categories yet)")
        return
    for cat in sorted(notes, key=str.lower):
        print("-", cat)
#---------------------------------------------------------------------------
def rename_category(notes: NotesDict, old: str, new: str) -> None:
    old = (old or "").strip().lower()
    new = (new or "General").strip().lower()

    if not old:
        print("No source category given.")
        return
    if old == new:
        print("Nothing to rename.")
        return

    try:
        src = notes.pop(old)   # what if old category doesn’t exist?
    except KeyError:
        print("No such category.")
        return

    notes.setdefault(new, []).extend(src)
    print(f"Renamed/moved {len(src)} note(s) from {old} → {new}.")
#--------------------------------------------------------------------------------
def merge_category(notes: NotesDict, source: str, target: str) -> None:
  # merging is just renaming source → target (append if target exists)
    rename_category(notes, source, target)
#------------------------------------------------------------------------------
def show_stats(notes: NotesDict) -> None:
    if not notes:
        print("(no notes yet)")
        return
    counts = {cat: len(items) for cat, items in notes.items()}
    total = sum(counts.values())
    for cat in sorted(counts, key=str.lower):
        print(f"{cat}: {counts[cat]} note(s)")
    print(f"Total: {total} note(s)")
#-------------------------------------------------------------------------------
def build_seen(notes: NotesDict) -> set[str]:
    """Return a set of normalized note texts from all notes."""
    s = set()
    for items in notes.values():
        for n in items:
            s.add(n.strip().lower())
    return s
#-------------------------------------------------------------------------------
def edit_note(notes: NotesDict, seen: set[str]):
    category = input("In which category would you like to edit a note? ").strip().lower()

    if category not in notes:
        print("Category not found!")
        return False

    cat_notes = notes[category]
    if not cat_notes:
        print(f"No notes in '{category}'.")
        return False

    print(f"\nNotes in '{category}':")
    show_numbered(cat_notes)

    # Step 3: safe index selection
    try:
        raw = input("\nWhich note would you like to edit?").strip()
        idx = int(raw)
        if not (1 <= idx <= len(cat_notes)):
            print("Invalid input! Please enter a number.")
            return False
        old_note = cat_notes[idx - 1] # Get the old note before asking for new text

    except ValueError:
        print("Invalid input. Please enter a number.")
        return False


    # Step 4: ask for new text
    new_text = input(f"New text for note '{old_note}': ").strip()
    if not new_text:
        print("Empty text canceled.")
        return False

    old_key = old_note.lower()
    new_key = new_text.lower()

    # no-op guard
    if new_key == old_key:
        print("No change- text is the same (case-insensitive).")
        return False
        
    #Duplicate  guard (anywher in the APP)
    exists_elsewhere = any(new_key in [n.strip().lower() for n in items] for items in notes.values())
    
    if exists_elsewhere:
        print("That text already exists. Edit canceled!.")
        return False

    # Confirm before mutating
    print(f"About to change: '{old_note}' → '{new_text}'")
    if not confirm("Apply edit? (y/n): "):
        print("Cancelled.")
        return False       

    # Mutate + sync seen
    cat_notes[idx - 1] = new_text
    seen.discard(old_key)
    seen.add(new_key)

    print(f"Updated note {idx} in '{category}': '{old_note}' → '{new_text}'")
    return True
    
#---------------------------------------------------------------------------------
def show_numbered(notes_list: list[str]):
    """Show a list of notes numbered 1, 2, 3..."""
    if not notes_list:
        print("  (no notes)")
        return
    for i, note in enumerate(notes_list, start=1):
        print(f"{i}. {note}")
#--------------------------------------------------------------------------------
def confirm(prompt: str) -> bool:
    ans= input(prompt).strip().lower()
    return ans == "y"
#--------------------------------------------------------------------------------
def list_unique_categories(notes: NotesDict)-> set[str]:
    categories = {cat for cat in notes}
    return categories
# ------------------------------
# Main loop
# ------------------------------

def main():
    notes, seen = load_notes()

    while True:
      show_menu()
      choice = input(">").strip()


      if choice == "1":
            text = input("Add a note: ").strip()
            cat  = input("Category (default: General): ").strip() or "General"
            add_note(notes, text, cat, seen)

      elif choice == "2":
            show_notes_grouped(notes)

      elif choice == "3":
            if not notes:
                print("No notes yet.")
                continue
            show_notes_grouped(notes)
            cat = input("Category to delete from: ").strip().lower()
            if cat not in notes:
                print("No such category.")
                continue
            try:
                idx = int(input("Number to delete (shown on the left): ").strip())
            except ValueError:
                print("Please type a number like 1 or 2.")
                continue

            removed = delete_note(notes, cat, idx, seen)
            if removed is not None:
                print(f" Deleted!: {removed!r}")

      elif choice == "4":
            term = input("search for note:").strip()
            search_notes(notes, term)

      elif choice == "5":
            moved = move_note(notes, seen)
            if moved is not None: 
               print(f"Moved {moved!r}")
                 
      elif choice == "6":
            list_categories(notes)

      elif choice == "7":
            old = input("Old category:").strip()
            new = input("New category:").strip()
            rename_category(notes, old, new)

      elif choice == "8":
            src = input("Merge from category:").strip()
            dst = input("Merge into category (Default: General):").strip() or "General"
            merge_category(notes, src, dst )
            show_notes_grouped(notes)

      elif choice == "9":
            show_stats(notes)

      elif choice == "10":
           changed = edit_note(notes, seen)
           if changed:
            save_notes(notes) # remove seen from save_notes call

      elif choice == "11":
            save_notes(notes)
            print("Saved. Bye!")
            break
      else:
            print("Choose 1-10.")

if __name__ == "__main__":
 main()

