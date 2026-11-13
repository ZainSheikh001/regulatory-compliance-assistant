import chromadb
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
DB_PATH = "chroma_db"
COLLECTION = "regulations"

embedder = SentenceTransformer(MODEL_NAME)
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_collection(COLLECTION)


def retrieve(question, top_k):
    """Return the top_k chunks whose meaning is closest to the question (from ChromaDB)."""
    q_vec = embedder.encode(question).tolist()
    res = collection.query(query_embeddings=[q_vec], n_results=top_k)

    results = []
    for i in range(len(res["ids"][0])):
        meta = res["metadatas"][0][i]
        results.append({
            "score": round(1 - res["distances"][0][i], 3),
            "section": meta["section"],
            "part": meta["part"],
            "text": res["documents"][0][i],
        })
    return results


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