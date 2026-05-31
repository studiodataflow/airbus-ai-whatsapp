import pandas as pd

df = pd.read_csv("airbus_pages_sample.csv")

for i in range(5):
    print("=" * 80)
    print(f"PAGE: {df.iloc[i]['page']}")
    print("=" * 80)
    print(df.iloc[i]['text'][:3000])
    print()