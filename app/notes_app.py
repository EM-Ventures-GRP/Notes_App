
"from os import remove"
import os, json
from typing import Dict, List
import re
from .utils import normalize
from .utils import load_notes_safe
from .utils import trace

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
 
def save_notes(notes: dict, filename: str = "data/notes.json") -> bool:
    """
    Safe save:
      1) ensure folder exists,
      2) write JSON to <filename>.tmp,
      3) os.replace(tmp, filename).
    Returns True on success, False on failure.
    """
    trace(f"enter save_notes ({filename})")

    # 1) ensure target folder exists
    folder = os.path.dirname(filename) or "."
    try:
        os.makedirs(folder, exist_ok=True)
    except Exception as e:
        trace(f"mkdir failed: {type(e).__name__}: {e}")
        return False

    # 2) write temp file
    tmp = filename + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(notes, f, indent=2)
    except Exception as e:
        trace(f"write tmp failed: {type(e).__name__}: {e}")
        # do not attempt replace if tmp write failed
        return False
    
    try:
        if os.path.exists(filename):
         bak = filename + ".bak"
        # keep last good file as backup (best-effort)
        try: os.replace(filename, bak)
        except Exception as e: trace(f"backup failed: {type(e).__name__}: {e}")
    except Exception as e:
     trace(f"pre-backup check failed: {type(e).__name__}: {e}")

    # 3) atomic replace
    try:
        os.replace(tmp, filename)
        trace("exit save_notes (ok)")
        return True
    except Exception as e:
        trace(f"replace failed: {type(e).__name__}: {e}")
        # best effort cleanup of tmp
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception as cleanup_err:
            trace(f"tmp cleanup failed: {type(cleanup_err).__name__}: {cleanup_err}")
        return False

#----------------------------------------------------------------------------------
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
    trace("enter add_note")

    category = (category or "General").strip().lower()
    text = text.strip()
    if not text:
        print("Empty note, cancelled.")
        return

    key = normalize(text)
    if key in seen:
        print("Duplicate note. Not added!")
        return


        # if no duplicate, add as usual
    notes.setdefault(category, []).append(text)
    seen.add(key)
    print(f"Note added to {category}.")
    trace("exit add_note")
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
    trace("enter delete_note")
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
    trace("exit delete_note")
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
    trace("enter move_note")
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
    trace("exit move_note")
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
            s.add(normalize(n))
    return s
#-------------------------------------------------------------------------------
def edit_note(notes: NotesDict, seen: set[str]):
    trace("enter edit_note")
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

    old_key = normalize(old_note)
    new_key = normalize(new_text)

    # no-op guard
    if new_key == old_key:
        print("No change- text is the same (case-insensitive).")
        return False
    
    all_keys = set()
    for _, items in notes.items():
        for n in items:
            all_keys.add(normalize(n))
    all_keys.discard(old_key) # allow replacing this note: we already checked

    if new_key in all_keys:
        print("That text already exists (normalized). Edit canceled!")
        return False     

    # Confirm before mutating
    print(f"About to change: '{old_note}' → '{new_text}'")
    if not confirm("Apply edit? (y/n): "):
        print("Cancelled.")
        return False       

    # Mutate + sync seen
    cat_notes[idx - 1] = new_text # keep the user's original text
    seen.discard(old_key)
    seen.add(new_key)

    print(f"Updated note {idx} in '{category}': '{old_note}' → '{new_text}'")
    trace("exit edit_note")
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
#--------------------------------------------------------------------------------
def category_counts(notes: NotesDict) -> dict[str, int]:
    counts = {cat : len(items) for cat, items in notes.items()}
    return counts
#--------------------------------------------------------------------------------
def category_note_lengths(notes: NotesDict) -> dict[str, int]:
    lengths = {cat: sum(len(n) for n in items) for cat, items in notes.items()}
    return lengths
#---------------------------------------------------------------------------------
def category_word_counts(notes: NotesDict, word: str) -> dict[str, int]:
    word = word.lower()
    counts = {}
    for cat, items in notes.items():
        counts[cat] = sum(1 for note in items if word in note.lower())
    return counts

# ------------------------------
# Main loop
# ------------------------------

def main():
    notes = load_notes_safe("notes.json")
    seen = build_seen(notes)

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

