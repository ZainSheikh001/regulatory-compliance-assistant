from retriever import retrieve
from answer import build_context

question = "What is the maximum credit balance allowed in an Asaan Account?"
top = retrieve(question, 5)

for r in top:
    print(r["score"], r["section"], "part", r["part"])
print("=" * 60)
print(build_context(top))