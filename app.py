import os
import requests
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from ask_manual_ai import answer_question

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "temporary-secret-key-change-this")
ACCESS_CODES = os.getenv("ACCESS_CODES", "TEST123").split(",")

# keep your existing HTML_PAGE and LOGIN_PAGE here unchanged


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

    return render_template_string(
        HTML_PAGE,
        question=question,
        answer=answer
    )


@app.route("/ask", methods=["GET", "POST"])
def ask():
    if not has_access():
        return jsonify({"error": "Access denied. Please log in first."}), 403

    if request.method == "GET":
        question = request.args.get("q", "")
    else:
        data = request.get_json()
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
        verify_token = "AIRBUS_VERIFY_TOKEN"

        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == verify_token:
            return challenge, 200

        return "Verification failed", 403

    if request.method == "POST":
        data = request.get_json()

        try:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            sender_phone = message["from"]
            user_question = message["text"]["body"]

            answer = answer_question(user_question)

            phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
            access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")

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
            print(response.text)

        except Exception as e:
            print("Webhook error:", e)

        return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )