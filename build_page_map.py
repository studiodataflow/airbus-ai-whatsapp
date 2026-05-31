import pandas as pd

bookmarks = pd.read_csv("airbus_bookmarks.csv")

bookmarks = bookmarks.sort_values("page")

page_map = []

for i in range(len(bookmarks)):
    current = bookmarks.iloc[i]

    start_page = int(current["page"])

    if i < len(bookmarks) - 1:
        end_page = int(bookmarks.iloc[i + 1]["page"]) - 1
    else:
        end_page = 5562

    for page in range(start_page, end_page + 1):
        page_map.append({
            "page": page,
            "level": current["level"],
            "section": current["title"]
        })

page_df = pd.DataFrame(page_map)

page_df.to_csv("page_section_map.csv", index=False)

print("Created page_section_map.csv")
print(f"Pages mapped: {len(page_df)}")
print(page_df.head(20))