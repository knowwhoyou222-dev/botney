from flask import Flask, request, jsonify
import json, time, os, secrets

app = Flask(__name__)

DB_FILE = "keys.json"
USE_DURATION = 300  # 5 λεπτά μετά το πρώτο use

# =========================
# DB
# =========================
def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# =========================
# GEN KEY (για bot)
# =========================
@app.route("/gen", methods=["POST"])
def gen():
    key = secrets.token_hex(16)

    db = load_db()

    db[key] = {
        "activated": False,
        "expiry": None
    }

    save_db(db)

    return jsonify({"key": key})

# =========================
# CHECK KEY (για scanner)
# =========================
@app.route("/check", methods=["POST"])
def check():
    data = request.json
    key = data.get("key")

    db = load_db()

    if key not in db:
        return jsonify({"status": "invalid"})

    entry = db[key]

    # 🔥 πρώτη χρήση
    if not entry.get("activated", False):
        entry["activated"] = True
        entry["expiry"] = int(time.time()) + USE_DURATION
        save_db(db)
        return jsonify({"status": "valid"})

    # 🔥 μετά την πρώτη χρήση
    if entry.get("expiry") and time.time() > entry["expiry"]:
        return jsonify({"status": "expired"})

    return jsonify({"status": "valid"})

# =========================
# RUN (Railway)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
