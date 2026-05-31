import pandas as pd

df = pd.read_parquet("airbus_knowledge_base.parquet")

print(df.head())
print(df.columns)