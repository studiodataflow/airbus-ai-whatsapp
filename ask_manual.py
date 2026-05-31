import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

df = pd.read_parquet("airbus_knowledge_base.parquet")

question = input("Ask a question about the Airbus manual: ")

keywords = question.lower().split()

df["score"] = df["text"].str.lower().apply(
    lambda text: sum(1 for word in keywords if word in text)
)

top_pages = df.sort_values("score", ascending=False).head(5)

context = ""

for _, row in top_pages.iterrows():
    context += f"""
SOURCE PAGE: {row['page']}
SECTION: {row['section']}
TEXT:
{row['text'][:3000]}
---
"""

prompt = f"""
You are an aviation study assistant for an A320/A321 student.

Use ONLY the provided Airbus FCOM context.
Do not guess.
If the answer is not clearly found, say:
"I could not find a clear answer in the provided manual."

Answer in this format:

Summary:
Student-friendly explanation:
Technical explanation:
Source:
- Manual: ABY A320/A321 FCOM
- Section:
- Page:
Important note:
This is for study only. Always follow official training material and instructor guidance.

Question:
{question}

Context:
{context}
"""

response = client.responses.create(
    model="gpt-4.1-mini",
    input=prompt
)

print("\n" + "=" * 80)
print(response.output_text)
print("=" * 80)

print("\nPages used:")
for _, row in top_pages.iterrows():
    print(f"Page {row['page']} | Section: {row['section']} | Score: {row['score']}")