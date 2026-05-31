import pickle

with open("airbus_chunks_metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

for item in metadata:

    if item["page"] == 2247:

        print("=" * 80)
        print("PAGE:", item["page"])
        print("SECTION:", item["section"])
        print()
        print(item["text"][:2000])

        break