from flask import Flask, request, jsonify
from ask_manual_ai import answer_question

app = Flask(__name__)


@app.route("/")
def home():
    return "Airbus Manual AI API is running."


@app.route("/ask", methods=["GET", "POST"])
def ask():
    if request.method == "GET":
        question = request.args.get("q", "")
    else:
        data = request.get_json()
        question = data.get("question", "")

    if not question:
        return jsonify({
            "error": "No question provided."
        }), 400

    answer = answer_question(question)

    return jsonify({
        "question": question,
        "answer": answer
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )