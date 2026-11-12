from pypdf import PdfReader

PDF_PATH = "data/onboarding_framework_2025.pdf"


def load_text(path, skip_pages):
    """Read every page after the first `skip_pages` pages into one text."""
    reader = PdfReader(path)
    text = ""
    for page in reader.pages[skip_pages:]:          # 👈 1: skip the first N pages
        text += page.extract_text() + "\n"          # 👈 2: add this page to the end
    return text


def remove_footers(text):
    """Drop every line that is a page footer like '6 | P a g e'."""
    clean_lines = []
    for line in text.split("\n"):
        if "| P a g e" not in line:                 # 👈 3: keep it only if it's NOT a footer
            clean_lines.append(line)                # 👈 4: add it to the list
    return "\n".join(clean_lines)                   # 👈 5: glue the lines back together


text = load_text(PDF_PATH, 2)
clean = remove_footers(text)

print("Characters before:", len(text))
print("Characters after:", len(clean))
print("Footers left:", clean.count("| P a g e"))
print("-" * 40)
print(clean[:500])