from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os, json
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

chat_history_path = "chat_history.json"
model = genai.GenerativeModel('gemini-pro')

# Load chat history
def load_history():
    if not os.path.exists(chat_history_path):
        return []
    with open(chat_history_path, "r") as file:
        return json.load(file)

# Save chat history
def save_history(history):
    with open(chat_history_path, "w") as file:
        json.dump(history, file, indent=2)

@app.route("/")
def index():
    history = load_history()
    return render_template("index.html", history=history)

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("message", "")
    if not user_input.strip():
        return jsonify({"response": "Please type something!"}), 400

    try:
        response = model.generate_content(user_input)
        bot_reply = response.text.strip()

        history = load_history()
        history.append({"role": "user", "text": user_input})
        history.append({"role": "bot", "text": bot_reply})
        save_history(history)

        return jsonify({"response": bot_reply})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"}), 500

@app.route("/clear", methods=["POST"])
def clear_history():
    save_history([])
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(debug=True)
