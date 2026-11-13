# Regulatory Compliance Assistant

A RAG (retrieval-augmented generation) assistant that answers compliance questions from regulatory documents **with section-level citations**, and says "I am not sure" instead of guessing when the answer isn't in the source.

**Dataset 1:** State Bank of Pakistan, *Consolidated Customer Onboarding Framework* (BPRD Circular No. 01 of 2025, 25 July 2025), a 21-page regulation covering account opening, digital onboarding, due diligence and account limits.

> Every bank, fintech and EMI must follow regulations like this, and rules change through amendments. Compliance teams search PDFs by hand. This project turns the regulation into a searchable, citable, verifiable assistant. The pipeline is regulator-agnostic; more jurisdictions are on the roadmap.

## Example

| Question | Answer | Citation |
|---|---|---|
| How many working days does a bank have to decide on an account opening request? | 2 working days for individuals, 5 for entities | Section I |
| Who is eligible for digital onboarding? | CNIC, NICOP, POC, POR or ARC holders | Section C |
| What is the interest rate on savings accounts? | *I am not sure.* (not covered by this regulation) | none |

## How it works

```
PDF -> extract text -> remove page footers -> chunk by section/annex -> split to <=800 chars (200 overlap)
    -> embed (all-MiniLM-L6-v2) -> retrieve top-5 by cosine similarity
    -> LLM answers ONLY from retrieved context, as JSON (Groq, gpt-oss-20b)
    -> guard validates the answer (Pydantic + citation checks)
```

**The guard rejects an answer if:**
1. the JSON has the wrong shape or types
2. it cites a section while claiming the question is unanswerable
3. it cites a section that was **not retrieved** for that question (catches invented citations)

## Engineering decisions (with evidence)

- **Structure-aware chunking instead of a generic splitter.** On this PDF, LangChain's `RecursiveCharacterTextSplitter` produced 118 chunks, kept the table of contents as a chunk, split rule I.1 across two chunks, and could only cite page numbers (three different page numbers for the same page). The custom chunker produces section-labelled chunks and skips the cover and contents.
- **Chunk size set by the embedding model's limit.** Section-level chunks (up to 8,000 characters) exceeded the model's ~256-token input limit, so paragraph C.5 was never embedded. Splitting to 800 characters with 200 overlap fixed it.
- **top_k = 5, chosen by measurement.** Debugging showed the correct chunk for one question ranked #4. Retrieval hit rate on the initial test questions: **hit@3 = 2/3 -> hit@5 = 3/3**.
- **Citations are validated against what was actually retrieved**, not a hard-coded list.

## Known issues (v0.1)

- Answers drawn from **table-heavy annexes** (e.g. Annex D, account limits) are **inconsistent across runs**: the same question sometimes gets the correct figure and sometimes "I am not sure". PDF tables are flattened into plain text.
- PDF text extraction leaves some broken or merged words (e.g. "c omplete", "ofthe").
- The initial test set is tiny (3-4 questions). A proper evaluation set is v0.2.

## Run it

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
copy .env.example .env            # then add your free Groq API key to .env
python src/answer.py
```

## Project structure

```
data/      source PDFs (public SBP documents)
src/       load_pdf.py -> chunker.py -> retriever.py -> answer.py
tests/     (v0.2)
eval/      (v0.2)
```

## Roadmap

- [x] **v0.1** Load, clean, chunk, retrieve, answer with citations, validate
- [ ] **v0.2** Evaluation set (30+ questions) with retrieval and answer-correctness metrics; table-aware chunking for annexes; re-ranker
- [ ] **v0.3** Vector database (ChromaDB), multiple circulars, metadata filters
- [ ] **v0.4** Amendment-aware answers (newer circulars override older ones, e.g. BPRD Circular Letter No. 09 of 2026)
- [ ] **v0.5** FastAPI backend + UI + Docker
- [ ] **v0.6** Deployment + CI (tests and eval on every push)
- [ ] Second jurisdiction (a Gulf regulator)

## Source and disclaimer

Source documents are published by the State Bank of Pakistan (sbp.org.pk). This is a portfolio/learning project, **not legal or compliance advice**. Always verify against the official circular.