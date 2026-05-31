import fitz
import pandas as pd

pdf_path = "airbuw_manual.pdf"

doc = fitz.open(pdf_path)

records = []

for page_num in range(min(20, doc.page_count)):
    page = doc[page_num]
    text = page.get_text()

    records.append({
        "page": page_num + 1,
        "text": text
    })

df = pd.DataFrame(records)

df.to_csv("airbus_pages_sample.csv", index=False)

print(f"Saved {len(df)} pages")