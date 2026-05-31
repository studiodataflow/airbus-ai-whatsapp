import pandas as pd

df = pd.read_parquet("airbus_topic_overlap_chunks.parquet")

print(df.head())

print("\nColumns:")
print(df.columns)

print("\nGreen System Pump chunks:")

green = df[df["topic"] == "Green System Pump"]

print(green[["page", "topic"]].head(10))

print("\nTotal Green System Pump chunks:")
print(len(green))