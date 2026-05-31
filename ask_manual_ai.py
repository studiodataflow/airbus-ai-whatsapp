import os
import pickle
import faiss
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

index = faiss.read_index("airbus_topic_faiss.index")

with open("airbus_topic_metadata.pkl", "rb") as f:
    metadata = pickle.load(f)


def detect_topic(text, fallback_section):
    text_upper = text.upper()

    topics = [
        "GREEN SYSTEM PUMP",
        "BLUE SYSTEM PUMPS",
        "YELLOW SYSTEM PUMPS",
        "POWER TRANSFER UNIT (PTU)",
        "RAM AIR TURBINE (RAT)",
        "RESERVOIR PRESSURIZATION",
        "SYSTEM ACCUMULATORS",
        "PRIORITY VALVES",
        "FIRE SHUTOFF VALVES",
        "LEAK MEASUREMENT VALVES",
        "FILTERS",
        "AUTOPILOT FUNCTION",
        "FLIGHT MODE",
        "AUTOLAND",
        "ILS APPROACH AND AUTOLAND",
    ]

    aliases = {
        "PTU": "POWER TRANSFER UNIT (PTU)",
        "RAT": "RAM AIR TURBINE (RAT)",
        "GREEN HYDRAULIC": "GREEN SYSTEM PUMP",
        "BLUE HYDRAULIC": "BLUE SYSTEM PUMPS",
        "YELLOW HYDRAULIC": "YELLOW SYSTEM PUMPS",
        "AUTOPILOT": "AUTOPILOT FUNCTION",
        "AUTOLAND SYSTEM": "AUTOLAND",
        "ILS": "ILS APPROACH AND AUTOLAND",
    }

    for alias, topic in aliases.items():
        if alias in text_upper:
            return topic.title()

    for topic in topics:
        if topic in text_upper:
            return topic.title()

    return fallback_section


def expand_question_for_search(question):
    prompt = f"""
Convert this Airbus A320/A321 question into useful FCOM search keywords.

Return only keywords.
No explanation.

Question:
{question}
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )
        keywords = response.output_text.strip()
        return f"{question}\n\n{keywords}"

    except Exception:
        return question


def search_manual(question, top_k=50):
    emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )

    query_vector = np.array([emb.data[0].embedding], dtype="float32")
    distances, indices = index.search(query_vector, top_k)

    results = []

    for rank, i in enumerate(indices[0]):
        if i == -1:
            continue

        item = metadata[i]

        section = str(item.get("section", "Unknown"))
        text = str(item.get("text", ""))

        if section.upper() == "GENERAL":
            continue

        topic = item.get("topic")
        if not topic:
            topic = detect_topic(text, section)

        score = float(distances[0][rank])

        results.append({
            "page": item.get("page", "Unknown"),
            "section": section,
            "topic": topic,
            "score": score,
            "text": text
        })

    results = sorted(results, key=lambda x: x["score"])
    return results[:15]


def filter_results_by_question(question, results):
    question_upper = question.upper()
    filtered_results = []

    filter_words = [
        "BLUE", "GREEN", "YELLOW", "PTU", "POWER TRANSFER",
        "RAT", "RAM AIR TURBINE", "AUTOPILOT",
        "AUTOLAND", "MANAGED", "MANUAL MODE"
    ]

    for item in results:
        topic_upper = item["topic"].upper()

        if "BLUE" in question_upper and "BLUE" in topic_upper:
            filtered_results.append(item)

        elif "GREEN" in question_upper and "GREEN" in topic_upper:
            filtered_results.append(item)

        elif "YELLOW" in question_upper and "YELLOW" in topic_upper:
            filtered_results.append(item)

        elif ("PTU" in question_upper or "POWER TRANSFER" in question_upper) and (
            "PTU" in topic_upper or "POWER TRANSFER" in topic_upper
        ):
            filtered_results.append(item)

        elif ("RAT" in question_upper or "RAM AIR TURBINE" in question_upper) and (
            "RAT" in topic_upper or "RAM AIR TURBINE" in topic_upper
        ):
            filtered_results.append(item)

        elif "AUTOPILOT" in question_upper and "AUTOPILOT" in topic_upper:
            filtered_results.append(item)

        elif "AUTOLAND" in question_upper and "AUTOLAND" in topic_upper:
            filtered_results.append(item)

        elif "MANAGED" in question_upper and "MANAGED" in topic_upper:
            filtered_results.append(item)

        elif "MANUAL MODE" in question_upper and "MANUAL MODE" in topic_upper:
            filtered_results.append(item)

        elif not any(word in question_upper for word in filter_words):
            filtered_results.append(item)

    return filtered_results


def remove_weak_matches(results, max_score=1.40):
    return [item for item in results if item["score"] <= max_score]


def remove_duplicates(results):
    seen = set()
    unique_results = []

    for item in results:
        key = (item["page"], item["topic"])

        if key not in seen:
            seen.add(key)
            unique_results.append(item)

    return unique_results


def answer_question(question):
    expanded_question = expand_question_for_search(question)

    results = search_manual(expanded_question, top_k=50)

    filtered_results = filter_results_by_question(question, results)
    filtered_results = remove_weak_matches(filtered_results, max_score=1.40)

    if filtered_results:
        results = filtered_results[:8]
    else:
        results = remove_weak_matches(results, max_score=1.40)[:8]

    results = remove_duplicates(results)

    context = ""

    for item in results:
        context += f"""
SOURCE PAGE: {item['page']}
SOURCE SECTION: {item['section']}
SOURCE TOPIC: {item['topic']}
TEXT:
{item['text']}
---
"""

    prompt = f"""
You are an Airbus A320/A321 training assistant.

Use ONLY the retrieved Airbus FCOM content as the source of truth.

Your job is to write the answer in clear ChatGPT-style language, but the facts must come from the retrieved FCOM content.

Rules:
- Use only information supported by the retrieved FCOM content.
- Do not invent facts.
- Do not use outside aviation knowledge.
- You should combine all relevant retrieved sections to answer the user's question completely.
- When a question asks about consequences, effects, failures, operations, or system interactions, use all relevant retrieved topics together.
- Do not answer from only one retrieved section if multiple sections contribute to the answer.
- Create a complete explanation using all retrieved evidence.
- If the retrieved content is not enough to answer fully, say what is missing.
- Write clearly, naturally, and professionally.
- Make the answer useful for a student pilot.

Answer format:

Answer:
[Give a clear direct answer.]

Explanation:
[Explain the answer in simple but accurate language.]

Source:
- Manual: ABY A320/A321 FCOM
- Topic:
- Page:

Question:
{question}

Retrieved FCOM content:
{context}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


if __name__ == "__main__":
    while True:
        question = input("\nAsk Airbus Manual AI (type exit to quit): ")

        if question.lower() == "exit":
            break

        answer = answer_question(question)

        print("\n" + "=" * 80)
        print(answer)
        print("=" * 80)