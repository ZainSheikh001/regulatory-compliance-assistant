# Regulatory Compliance Assistant

A RAG (retrieval-augmented generation) assistant that answers compliance questions from regulatory documents **with section-level citations**, and says "I am not sure" instead of guessing when the answer isn't in the source.

**Dataset 1:** State Bank of Pakistan, *Consolidated Customer Onboarding Framework* (BPRD Circular No. 01 of 2025, 25 July 2025), a 21-page regulation covering account opening, digital onboarding, due diligence and account limits.

> Every bank, fintech and EMI must follow regulations like this, and rules change through amendments. Compliance teams search PDFs by hand. This project turns the regulation into a searchable, citable, verifiable assistant. The pipeline is regulator-agnostic; more jurisdictions are on the roadmap.

## Results (v0.2 evaluation)

Evaluated on a 14-question golden set (12 answerable, 2 deliberately unanswerable), built from and verified against the source PDF.

| Metric | Score |
|---|---|
| Section hit @5 (right section retrieved) | 12 / 12 |
| Context hit @5 (answer text actually retrieved) | 9 / 12 |
| **Answer accuracy** | **11 / 14 (79%)** |
| Guard verdicts valid | 14 / 14 |
| **Confident wrong answers** | **0** |

**Key finding:** when the answer text was in the retrieved context, the model answered correctly **9 / 9** times. All 3 failures were honest "I am not sure" refusals caused by retrieval misses on table-heavy content, so the bottleneck is retrieval, not generation.

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

- **Structure-aware chunking instead of a generic splitter.** On this PDF, LangChain's `RecursiveCharacterTextSplitter` produced 118 chunks, kept the table of contents as a chunk, split rule I.1 across two chunks, and could only cite page numbers. The custom chunker produces section-labelled chunks and skips the cover and contents.
- **Chunk size set by the embedding model's limit.** Section-level chunks (up to 8,000 characters) exceeded the model's ~256-token input limit, so paragraph C.5 was never embedded. Splitting to 800 characters with 200 overlap fixed it.
- **Two retrieval metrics, because one was misleading.** Section-level hit rate reported 12/12 while answers still failed: the right section was found but the wrong chunk of it. A context-level metric (is the answer text in the retrieved context?) exposed the real rate, 9/12.
- **Bigger model tested, rejected.** Switching from `gpt-oss-20b` to `gpt-oss-120b` gave the same accuracy (the missing information was never in the context), so the smaller, faster model was kept.
- **top_k = 5, not 10: precision over recall.** top_k = 10 raised context hit to 12/12 but introduced a confident wrong answer (PKR 1,000,000 instead of 3,000,000 for an Asaan Account) from noisy table text. In compliance, an honest refusal is safer than a wrong figure.
- **A robust grader.** The evaluator normalises Unicode look-alikes (non-breaking spaces and hyphens) after these caused false failures.

## Known issues

- **Table-heavy annexes** (e.g. Annex D, account limits) are flattened into plain text by PDF extraction, so their rows retrieve poorly. This causes all 3 current failures.
- PDF text extraction leaves some broken or merged words (e.g. "c omplete", "ofthe").
- The golden set is small (14 questions); results will be re-measured as it grows.

## Run it

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
copy .env.example .env            # then add your free Groq API key to .env
python src/answer.py              # ask the example questions
python eval/run_eval.py           # run the evaluation
```

## Project structure

```
data/      source PDFs (public SBP documents)
src/       load_pdf.py -> chunker.py -> retriever.py -> answer.py
eval/      golden_set.json (questions + expected answers), run_eval.py (scoring)
tests/     (planned)
```

## Roadmap

- [x] **v0.1** Load, clean, chunk, retrieve, answer with citations, validate
- [x] **v0.2** Golden-set evaluation with section, context and answer metrics
- [ ] **v0.2.1** Fix table retrieval: re-ranker and/or table-aware chunking for annexes
- [ ] **v0.3** Vector database (ChromaDB), multiple circulars, metadata filters
- [ ] **v0.4** Amendment-aware answers (newer circulars override older ones, e.g. BPRD Circular Letter No. 09 of 2026)
- [ ] **v0.5** FastAPI backend + UI + Docker
- [ ] **v0.6** Deployment + CI (tests and eval on every push)
- [ ] Second jurisdiction (a Gulf regulator)

## Source and disclaimer

Source documents are published by the State Bank of Pakistan (sbp.org.pk). This is a portfolio/learning project, **not legal or compliance advice**. Always verify against the official circular.