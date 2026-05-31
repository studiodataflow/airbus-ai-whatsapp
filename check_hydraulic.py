import pandas as pd

df = pd.read_parquet("airbus_knowledge_base.parquet")

row = df[df["page"] == 2247]

print(row.iloc[0]["text"])