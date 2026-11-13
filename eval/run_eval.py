import json
import sys
import unicodedata

sys.path.insert(0, "src")
from answer import answer, CiteAnswer, build_context, TOP_K
from retriever import retrieve

GOLDEN_PATH = "eval/golden_set.json"


def normalize(text):
    """Turn look-alike characters (special spaces, hyphens) into plain ones, then lowercase."""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u2010", "-").replace("\u2011", "-")
    return text.lower()


def contains_all(answer_text, must_contain):
    """True if the answer has at least one word from EVERY group in must_contain."""
    text = normalize(answer_text)
    for group in must_contain:
        found = False
        for word in group:
            if normalize(word) in text:
                found = True
        if not found:
            return False
    return True


with open(GOLDEN_PATH, encoding="utf-8") as f:
    golden = json.load(f)

section_hits = 0
context_hits = 0
answerable_count = 0
correct_count = 0
valid_count = 0

for item in golden:
    raw, verdict, allowed = answer(item["question"])

    try:
        result = CiteAnswer.model_validate_json(raw)
    except Exception:
        result = None

    if item["answerable"]:
        answerable_count += 1
        section_hit = item["expected_section"] in allowed
        context = build_context(retrieve(item["question"], TOP_K))
        context_hit = contains_all(context, item["must_contain"])
        if section_hit:
            section_hits += 1
        if context_hit:
            context_hits += 1
    else:
        section_hit = None
        context_hit = None

    if result is None:
        correct = False
    elif item["answerable"]:
        correct = result.is_answerable and contains_all(result.answer, item["must_contain"])
    else:
        correct = not result.is_answerable

    if correct:
        correct_count += 1
    if verdict == "Valid":
        valid_count += 1

    def mark(x):
        return "-" if x is None else ("OK" if x else "MISS")

    print(item["id"], "| section:", mark(section_hit), "| context:", mark(context_hit),
          "| answer:", "OK" if correct else "WRONG", "| guard:", verdict)
    if not correct and result is not None:
        print("      got:", result.answer)
    if verdict != "Valid":
        print("      raw:", raw)
        print("      allowed:", allowed)

total = len(golden)
print("=" * 70)
print("Section hit @5 (right section name):   ", section_hits, "/", answerable_count)
print("Context hit @5 (answer text retrieved):", context_hits, "/", answerable_count)
print("Answer accuracy:                       ", correct_count, "/", total)
print("Guard verdicts Valid:                  ", valid_count, "/", total)