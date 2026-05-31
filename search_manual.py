import os
import pickle
import faiss
import numpy as np

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Loading FAISS chunk index...")
index = faiss.read_index("airbus_chunks_faiss.index")

print("Loading chunk metadata...")
with open("airbus_chunks_metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

print("Ready.")


def search_manual(question, top_k=40):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )

    query_embedding = np.array(
        [response.data[0].embedding],
        dtype="float32"
    )

    distances, indices = index.search(query_embedding, top_k)

    results = []

    for rank, i in enumerate(indices[0]):
        if i == -1:
            continue

        item = metadata[i]

        section = str(item.get("section", "Unknown"))
        text = str(item.get("text", ""))

        if section.upper() == "GENERAL":
            continue

        score = float(distances[0][rank])

        results.append({
            "page": item.get("page", "Unknown"),
            "section": section,
            "score": score,
            "text": text
        })

    results = sorted(results, key=lambda x: x["score"])
    results = results[:15]

    return results


while True:
    question = input("\nAsk Airbus Manual (type exit to quit): ")

    if question.lower() == "exit":
        break

    results = search_manual(question, top_k=40)

    print("\nRETRIEVED CHUNKS:\n")

    for i, result in enumerate(results, start=1):
        print("=" * 80)
        print(f"Result {i}")
        print(f"Page: {result['page']}")
        print(f"Section: {result['section']}")
        print(f"Score: {result['score']:.2f}")
        print("-" * 80)
        print(result["text"][:1500])