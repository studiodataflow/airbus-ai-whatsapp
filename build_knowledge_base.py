import fitz
import pandas as pd

pdf_path = "airbuw_manual.pdf"

doc = fitz.open(pdf_path)

page_map = pd.read_csv("page_section_map.csv")

records = []

for page_num in range(doc.page_count):

    text = doc[page_num].get_text()

    section_row = page_map[
        page_map["page"] == page_num + 1
    ]

    if len(section_row) > 0:
        section = section_row.iloc[0]["section"]
    else:
        section = "Unknown"

    records.append({
        "page": page_num + 1,
        "section": section,
        "text": text[:10000]
    })

    if (page_num + 1) % 500 == 0:
        print(f"Processed {page_num + 1} pages")

df = pd.DataFrame(records)

df.to_parquet(
    "airbus_knowledge_base.parquet",
    index=False
)

print()
print("Knowledge base created")
print(f"Total pages: {len(df)}")