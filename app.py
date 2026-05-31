import os
import requests
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from ask_manual_ai import answer_question

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "temporary-secret-key-change-this")
ACCESS_CODES = os.getenv("ACCESS_CODES", "TEST123").split(",")

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Airbus Manual AI</title>
    <style>
        body { font-family: Arial, sans-serif; background:#f4f6f8; padding:40px; }
        .container { max-width:850px; margin:auto; background:white; padding:30px; border-radius:16px; box-shadow:0 4px 18px rgba(0,0,0,0.08); }
        h1 { text-align:center; color:#102a43; }
        textarea, input { width:100%; padding:14px; font-size:16px; border-radius:10px; border:1px solid #ccc; }
        textarea { height:90px; resize:vertical; }
        button { margin-top:15px; width:100%; padding:14px; background:#0b5ed7; color:white; border:none; border-radius:10px; font-size:17px; cursor:pointer; }
        .answer { margin-top:25px; padding:20px; background:#f8fafc; border-left:5px solid #0b5ed7; white-space:pre-wrap; line-height:1.6; }
        .note { text-align:center; color:#6b7280; font-size:14px; margin-top:15px; }
        .logout { text-align:right; font-size:14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logout"><a href="/logout">Logout</a></div>
        <h1>Airbus Manual AI Study Assistant</h1>
        <form method="POST">
            <textarea name="question" placeholder="Ask a question, for example: What is PTU?" required>{{ question }}</textarea>
            <button type="submit">Ask Airbus AI</button>
        </form>
        {% if answer %}
        <div class="answer">{{ answer }}</div>
        {% endif %}
        <div class="note">Study support only. Always follow official training material and instructor guidance.</div>
    </div>
</body>
</html>
"""

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Access Airbus Manual AI</title>
    <style>
        body { font-family: Arial, sans-serif; background:#f4f6f8; padding:40px; }
        .container { max-width:500px; margin:auto; background:white; padding:30px; border-radius:16px; box-shadow:0 4px 18px rgba(0,0,0,0.08); }
        h1 { text-align:center; color:#102a43; }
        input { width:100%; padding:14px; font-size:16px; border-radius:10px; border:1px solid #ccc; }
        button { margin-top:15px; width:100%; padding:14px; background:#0b5ed7; color:white; border:none; border-radius:10px; font-size:17px; cursor:pointer; }
        .note { text-align:center; color:#6b7280; font-size:14px; margin-top:15px; }
        .error { color:#b00020; margin-top:15px; text-align:center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Private Access</h1>
        <p class="note">Enter your approved access code to use the Airbus Manual AI Study Assistant.</p>
        <form method="POST">
            <input name="access_code" placeholder="Enter access code" required>
            <button type="submit">Enter</button>
        </form>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <div class="note">Access is for approved students only.</div>
    </div>
</body>
</html>
"""


def has_access():
    return session.get("approved") is True


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        entered_code = request.form.get("access_code", "").strip()
        clean_codes = [code.strip() for code in ACCESS_CODES]

        if entered_code in clean_codes:
            session["approved"] = True
            return redirect(url_for("home"))
        else:
            error = "Invalid access code. Please request access from the owner."

    return render_template_string(LOGIN_PAGE, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
def home():
    if not has_access():
        return redirect(url_for("login"))

    answer = ""
    question = ""

    if request.method == "POST":
        question = request.form.get("question", "")
        if question:
            answer = answer_question(question)

    return render_template_string(HTML_PAGE, question=question, answer=answer)


@app.route("/ask", methods=["GET", "POST"])
def ask():
    if request.method == "GET":
        question = request.args.get("q", "")
    else:
        data = request.get_json() or {}
        question = data.get("question", "")

    if not question:
        return jsonify({"error": "No question provided."}), 400

    answer = answer_question(question)

    return jsonify({
        "question": question,
        "answer": answer
    })


@app.route("/webhook", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        verify_token = os.getenv("VERIFY_TOKEN", "AIRBUS_VERIFY_TOKEN")

        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == verify_token:
            return challenge, 200

        return "Verification failed", 403

    if request.method == "POST":
        data = request.get_json()
        print("WhatsApp webhook received:", data)

        try:
            value = data["entry"][0]["changes"][0]["value"]

            if "messages" not in value:
                return "EVENT_RECEIVED", 200

            message = value["messages"][0]

            if message.get("type") != "text":
                user_question = "Please send a text question."
            else:
                user_question = message["text"]["body"]

            sender_phone = message["from"]

            answer = answer_question(user_question)

            phone_number_id = os.getenv("PHONE_NUMBER_ID")
            access_token = os.getenv("WHATSAPP_TOKEN")

            url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "messaging_product": "whatsapp",
                "to": sender_phone,
                "type": "text",
                "text": {
                    "body": answer[:4000]
                }
            }

            response = requests.post(url, headers=headers, json=payload)
            print("WhatsApp send status:", response.status_code)
            print("WhatsApp response:", response.text)

        except Exception as e:
            print("Webhook error:", e)

        return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)