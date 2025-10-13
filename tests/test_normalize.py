from app.utils import normalize

def test_variants_collapse_to_same():
    samples = ["To-do", " to do  ", "TO   DO!!"]
    keys = {normalize(s) for s in samples}
    assert keys == {"to do"}

def test_numbers_and_text():
    assert normalize("Budget-2025!!  ") == "budget 2025"
