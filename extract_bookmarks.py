import fitz
import pandas as pd

pdf_path = "airbuw_manual.pdf"
doc = fitz.open(pdf_path)

toc = doc.get_toc(simple=False)

records = []

for item in toc:
    level = item[0]
    title = item[1]
    page = item[2]

    records.append({
        "level": level,
        "title": title,
        "page": page
    })

df = pd.DataFrame(records)
df.to_csv("airbus_bookmarks.csv", index=False)

print(f"Total bookmarks found: {len(df)}")
print("Saved: airbus_bookmarks.csv")

print("\nFirst 30 bookmarks:")
print(df.head(30))