import os
import time
import pickle
import numpy as np
import pandas as pd
import faiss

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

df = pd.read_parquet("airbus_knowledge_base.parquet")

texts = []
metadata = []

for _, row in df.iterrows():
    text = f"""
Manual: ABY A320/A321 FCOM
Page: {row['page']}
Section: {row['section']}

{row['text']}
"""
    texts.append(text[:7000])
    metadata.append({
        "page": int(row["page"]),
        "section": str(row["section"]),
        "text": str(row["text"])
    })

embeddings = []

batch_size = 50

for i in range(0, len(texts), batch_size):
    batch = texts[i:i + batch_size]

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=batch
    )

    batch_embeddings = [item.embedding for item in response.data]
    embeddings.extend(batch_embeddings)

    print(f"Embedded {min(i + batch_size, len(texts))} / {len(texts)} pages")
    time.sleep(0.2)

embeddings_np = np.array(embeddings).astype("float32")

dimension = embeddings_np.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings_np)

faiss.write_index(index, "airbus_faiss.index")

with open("airbus_metadata.pkl", "wb") as f:
    pickle.dump(metadata, f)

print()
print("Embeddings created successfully")
print(f"Total vectors: {index.ntotal}")
print("Saved: airbus_faiss.index")
print("Saved: airbus_metadata.pkl")