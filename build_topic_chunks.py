import pandas as pd
import fitz

pdf_path = "airbuw_manual.pdf"

doc = fitz.open(pdf_path)
bookmarks = pd.read_csv("airbus_bookmarks.csv")

topic_rows = bookmarks[bookmarks["level"] == 5].copy()
topic_rows = topic_rows.reset_index(drop=True)

chunks = []

for idx, row in topic_rows.iterrows():

    page = int(row["page"])
    topic = str(row["title"])

    page_text = doc[page - 1].get_text()

    start_pos = page_text.upper().find(topic.upper())

    if start_pos == -1:
        topic_text = page_text
    else:
        next_pos = len(page_text)

        same_page_next_topics = topic_rows[
            (topic_rows["page"] == page) &
            (topic_rows.index > idx)
        ]

        for _, next_row in same_page_next_topics.iterrows():
            next_topic = str(next_row["title"])
            found_pos = page_text.upper().find(next_topic.upper(), start_pos + 1)

            if found_pos != -1:
                next_pos = found_pos
                break

        topic_text = page_text[start_pos:next_pos]

    chunks.append({
        "page": page,
        "topic": topic,
        "section": topic,
        "text": topic_text
    })

chunk_df = pd.DataFrame(chunks)

chunk_df.to_parquet(
    "airbus_topic_chunks.parquet",
    index=False
)

print("Topic chunks created:", len(chunk_df))
print("Saved: airbus_topic_chunks.parquet")