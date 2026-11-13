import chromadb
from sentence_transformers import SentenceTransformer
from load_pdf import PDF_PATH, load_text, remove_footers
from chunker import chunk_by_section, split_big_chunks

MODEL_NAME = "all-MiniLM-L6-v2"
DB_PATH = "chroma_db"
COLLECTION = "regulations"


def build_index():
    """Load -> clean -> chunk -> embed -> save everything into ChromaDB on disk."""
    embedder = SentenceTransformer(MODEL_NAME)
    sections = chunk_by_section(remove_footers(load_text(PDF_PATH, 2)))
    chunks = split_big_chunks(sections, 800, 200)

    client = chromadb.PersistentClient(path=DB_PATH)
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    collection = client.create_collection(name=COLLECTION, metadata={"hnsw:space": "cosine"})

    ids = []
    texts = []
    metadatas = []
    for i in range(len(chunks)):
        c = chunks[i]
        ids.append("bprd-c1-2025-" + str(i))
        texts.append(c["text"])
        metadatas.append({"section": c["section"], "part": c["part"], "source": c["source"], "date": c["date"]})

    embeddings = embedder.encode(texts).tolist()
    collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
    print("Indexed", collection.count(), "chunks into", DB_PATH)


if __name__ == "__main__":
    build_index()