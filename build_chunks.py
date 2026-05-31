import pandas as pd

# Load existing knowledge base
df = pd.read_parquet("airbus_knowledge_base.parquet")

chunks = []

for _, row in df.iterrows():

    text = str(row["text"])

    chunk_size = 500
    overlap = 100

    for i in range(0, len(text), chunk_size - overlap):

        chunk_text = text[i:i + chunk_size]

        chunks.append({
            "page": row["page"],
            "section": row["section"],
            "text": chunk_text
        })

chunk_df = pd.DataFrame(chunks)

chunk_df.to_parquet(
    "airbus_chunks.parquet",
    index=False
)

print("Chunks created:", len(chunk_df))
print("Saved: airbus_chunks.parquet")