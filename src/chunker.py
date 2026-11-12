from load_pdf import PDF_PATH, load_text, remove_footers

SOURCE = "SBP BPRD Circular No. 01 of 2025 - Consolidated Customer Onboarding Framework"
DATE = "2025-07-25"


def is_section_heading(line):
    """True for lines like 'I. Turn-Around-Time (TAT)'."""
    return len(line) > 3 and line[0] in "ABCDEFGHIJK" and line[1:3] == ". "


def chunk_by_section(text):
    """One chunk per lettered section (A to K)."""
    chunks = []
    current = None

    for line in text.split("\n"):
        line = line.strip()

        if line.startswith("Annex - A"):
            break

        if is_section_heading(line):
            if current is not None:
                chunks.append(current)
            current = {"section": "Section " + line[0], "text": line, "source": SOURCE, "date": DATE}

        elif line != "" and current is not None:
            current["text"] += " " + line

    if current is not None:
        chunks.append(current)
    return chunks


if __name__ == "__main__":
    text = remove_footers(load_text(PDF_PATH, 2))
    chunks = chunk_by_section(text)
    print("Number of chunks:", len(chunks))
    for c in chunks:
        print(c["section"], "|", len(c["text"]), "characters |", c["text"][:60])