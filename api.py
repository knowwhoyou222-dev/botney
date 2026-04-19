from flask import Flask, request, jsonify
import json, time, os, secrets

app = Flask(__name__)

DB_FILE = "keys.json"

# ⏳ διάρκεια μετά το πρώτο use (π.χ. 5 λεπτά)
USE_DURATION = 300


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
        "hwid": None,
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
    hwid = data.get("hwid")

    db = load_db()

    if key not in db:
        return jsonify({"status": "invalid"})

    entry = db[key]

    # 🔒 HWID CHECK
    if entry["hwid"] and entry["hwid"] != hwid:
        return jsonify({"status": "invalid_hwid"})

    # 🔥 FIRST USE
    if not entry["activated"]:
        entry["activated"] = True
        entry["hwid"] = hwid
        entry["expiry"] = int(time.time()) + USE_DURATION
        save_db(db)
        return jsonify({"status": "valid"})

    # 🔥 AFTER USE → expiry check
    if entry["expiry"] and time.time() > entry["expiry"]:
        return jsonify({"status": "expired"})

    # 🔥 SECOND USE (same PC)
    return jsonify({"status": "used"})


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
