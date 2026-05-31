import pandas as pd

df = pd.read_csv("airbus_bookmarks.csv")

page = 2247

nearby = df[
    (df["page"] >= page - 20) &
    (df["page"] <= page + 20)
]

print(nearby.to_string())