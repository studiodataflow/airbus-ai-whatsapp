import pandas as pd

df = pd.read_parquet("airbus_knowledge_base.parquet")

print("Rows:", len(df))

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst row:")
print(df.iloc[0])

print("\nPage 2247:")
page = df[df["page"] == 2247]

if len(page):
    print(page.iloc[0]["section"])
    print("\nText length:", len(page.iloc[0]["text"]))
    print("\nFirst 1000 characters:\n")
    print(page.iloc[0]["text"][:1000])