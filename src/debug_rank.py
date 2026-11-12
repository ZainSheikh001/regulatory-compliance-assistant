from retriever import retrieve

question = "Who is eligible for digital onboarding?"
results = retrieve(question, 74)

for rank, r in enumerate(results, 1):
    if r["section"] == "Section C":
        print("Rank", rank, "| score", r["score"], "|", r["section"], "part", r["part"])