import pandas as pd

df = pd.read_csv("airbus_bookmarks.csv")

result = df[df["page"] == 2247]

print(result)