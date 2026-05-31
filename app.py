from flask import Flask, request, jsonify, render_template_string
from ask_manual_ai import answer_question

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Airbus Manual AI</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            margin: 0;
            padding: 40px;
        }
        .container {
            max-width: 850px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 4px 18px rgba(0,0,0,0.08);
        }
        h1 {
            text-align: center;
            color: #102a43;
        }
        textarea {
            width: 100%;
            height: 90px;
            padding: 14px;
            font-size: 16px;
            border-radius: 10px;
            border: 1px solid #ccc;
            resize: vertical;
        }
        button {
            margin-top: 15px;
            width: 100%;
            padding: 14px;
            background: #0b5ed7;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 17px;
            cursor: pointer;
        }
        button:hover {
            background: #084db3;
        }
        .answer {
            margin-top: 25px;
            padding: 20px;
            background: #f8fafc;
            border-left: 5px solid #0b5ed7;
            white-space: pre-wrap;
            line-height: 1.6;
        }
        .note {
            text-align: center;
            color: #6b7280;
            font-size: 14px;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Airbus Manual AI Study Assistant</h1>

        <form method="POST">
            <textarea name="question" placeholder="Ask a question, for example: What is PTU?" required>{{ question }}</textarea>
            <button type="submit">Ask Airbus AI</button>
        </form>

        {% if answer %}
        <div class="answer">{{ answer }}</div>
        {% endif %}

        <div class="note">
            Study support only. Always follow official training material and instructor guidance.
        </div>
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    answer = ""
    question = ""

    if request.method == "POST":
        question = request.form.get("question", "")
        if question:
            answer = answer_question(question)

    return render_template_string(
        HTML_PAGE,
        question=question,
        answer=answer
    )


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