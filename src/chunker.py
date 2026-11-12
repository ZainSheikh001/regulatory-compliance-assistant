from load_pdf import PDF_PATH, load_text, remove_footers

SOURCE = "SBP BPRD Circular No. 01 of 2025 - Consolidated Customer Onboarding Framework"
DATE = "2025-07-25"


def is_section_heading(line):
    """True for lines like 'I. Turn-Around-Time (TAT)'."""
    return len(line) > 3 and line[0] in "ABCDEFGHIJK" and line[1:3] == ". "


def chunk_by_section(text):
    """One chunk per lettered section (A to K), then one chunk per annex (A to D)."""
    chunks = []
    current = None
    in_annexes = False

    for line in text.split("\n"):
        line = line.strip()

        if line.startswith("Annex - A"):
            in_annexes = True

        if in_annexes and line.startswith("Annex - "):
            if current is not None:
                chunks.append(current)
            current = {"section": "Annex " + line[8], "heading": line, "text": line, "source": SOURCE, "date": DATE}

        elif not in_annexes and is_section_heading(line):
            if current is not None:
                chunks.append(current)
            current = {"section": "Section " + line[0], "heading": line, "text": line, "source": SOURCE, "date": DATE}

        elif line != "" and current is not None:
            current["text"] += " " + line

    if current is not None:
        chunks.append(current)
    return chunks


def split_big_chunks(chunks, size, overlap):
    """Cut any chunk longer than `size` into overlapping pieces. Each piece keeps its section."""
    pieces = []
    for chunk in chunks:
        text = chunk["text"]
        part = 1
        for start in range(0, len(text), size - overlap):
            piece = text[start:start + size]
            pieces.append({
                "section": chunk["section"],
                "part": part,
                "text": chunk["heading"] + " > " + piece,
                "source": chunk["source"],
                "date": chunk["date"],
            })
            part += 1
            if start + size >= len(text):
                break
    return pieces


if __name__ == "__main__":
    text = remove_footers(load_text(PDF_PATH, 2))
    sections = chunk_by_section(text)
    chunks = split_big_chunks(sections, 800, 200)
    print("Sections:", len(sections))
    print("Chunks after splitting:", len(chunks))
    for c in chunks:
        print(c["section"], "part", c["part"], "|", len(c["text"]), "characters")