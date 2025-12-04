# server.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# load .env
load_dotenv()

# ensure GROQ key present; query.py already enforces this but fail early
if not os.getenv("GROQ_API_KEY"):
    print("WARNING: GROQ_API_KEY not set in environment. Ensure .env or env var exists.")

# Import your existing code (assumes query.py defines ask() and ingest.build_index)
from query import ask
from ingest import build_index

app = Flask(__name__)
CORS(app)

@app.route("/api/ask", methods=["POST"])
def api_ask():
    payload = request.json or {}
    question = payload.get("question", "").strip()
    if not question:
        return jsonify({"error": "question required"}), 400

    try:
        # ask() returns a string (model reply). If you enhanced ask to return structured info,
        # adjust this to return that structure (answer, citations, chunk_ids, etc.)
        answer = ask(question)
        return jsonify({"answer": answer})
    except Exception as e:
        # don't leak sensitive internals, but include the message
        return jsonify({"error": str(e)}), 500

@app.route("/api/rebuild", methods=["POST"])
def api_rebuild():
    try:
        build_index()
        return jsonify({"status": "ok", "message": "Index rebuilt."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # dev server
    port = int(os.getenv("API_PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
