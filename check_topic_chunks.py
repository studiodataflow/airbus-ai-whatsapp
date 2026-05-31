import pandas as pd

df = pd.read_parquet("airbus_topic_chunks.parquet")

print(df.head())

print("\nColumns:")
print(df.columns)

print("\nGreen System Pump:")

print(
    df[df["topic"] == "Green System Pump"]
)