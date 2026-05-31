import pandas as pd

df = pd.read_csv("page_section_map.csv")

print(df.head())
print(df.columns)

print("\nRows for page 2247:")
print(df[df["page"] == 2247])