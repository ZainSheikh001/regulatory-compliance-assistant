from sentence_transformers import SentenceTransformer, util
from load_pdf import PDF_PATH, load_text, remove_footers
from chunker import chunk_by_section, split_big_chunks

MODEL_NAME = "all-MiniLM-L6-v2"

# ---------- INDEXING: done once, when this file loads ----------
embedder = SentenceTransformer(MODEL_NAME)
sections = chunk_by_section(remove_footers(load_text(PDF_PATH, 2)))
chunks = split_big_chunks(sections, 800, 200)

chunk_texts = []
for chunk in chunks:
    chunk_texts.append(chunk["text"])
chunk_vecs = embedder.encode(chunk_texts)


# ---------- RETRIEVAL: done for every question ----------
def retrieve(question, top_k):
    """Return the top_k chunks whose meaning is closest to the question."""
    q_vec = embedder.encode(question)
    scores = util.cos_sim(q_vec, chunk_vecs)[0]
    results = []
    for i in range(len(chunks)):
        results.append({
            "score": round(float(scores[i]), 3),
            "section": chunks[i]["section"],
            "part": chunks[i]["part"],
            "text": chunks[i]["text"],
        })
    results = sorted(results, key=lambda r: r["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    questions = [
        "How many working days does a bank have to decide on an account opening request?",
        "Who is eligible for digital onboarding?",
        "What is the maximum balance allowed in an Asaan Account?",
    ]
    for q in questions:
        print("QUESTION:", q)
        for r in retrieve(q, 5):
            print("   ", r["score"], r["section"], "part", r["part"])
        print("-" * 50)