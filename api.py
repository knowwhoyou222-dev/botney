from flask import Flask, request, jsonify
import json, time, os, secrets

app = Flask(__name__)

db = {}  # προσωρινό (memory)

USE_DURATION = 300

# =========================
# GEN KEY
# =========================
@app.route("/gen", methods=["POST"])
def gen():
    key = secrets.token_hex(16)

    db[key] = {
        "activated": False,
        "expiry": None
    }

    return jsonify({"key": key})

# =========================
# CHECK KEY
# =========================
@app.route("/check", methods=["POST"])
def check():
    data = request.json
    key = data.get("key")

    if key not in db:
        return jsonify({"status": "invalid"})

    entry = db[key]

    if not entry["activated"]:
        entry["activated"] = True
        entry["expiry"] = int(time.time()) + USE_DURATION
        return jsonify({"status": "valid"})

    if entry["expiry"] and time.time() > entry["expiry"]:
        return jsonify({"status": "expired"})

    return jsonify({"status": "valid"})

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
