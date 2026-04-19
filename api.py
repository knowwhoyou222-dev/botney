from flask import Flask, request, jsonify
import time, os, secrets, requests

app = Flask(__name__)

db = {}

USE_DURATION = 300  # optional (μπορείς να το αφαιρέσεις αν θες instant burn)

WEBHOOK = "ΒΑΛΕ_WEBHOOK_URL"

def log(msg):
    try:
        requests.post(WEBHOOK, json={"content": msg})
    except:
        pass

@app.route("/gen", methods=["POST"])
def gen():
    key = secrets.token_hex(16)

    db[key] = {
        "activated": False,
        "hwid": None,
        "used": False,
        "expiry": None
    }

    log(f"🆕 New Key Generated: `{key}`")

    return jsonify({"key": key})

@app.route("/check", methods=["POST"])
def check():
    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")

    if key not in db:
        return jsonify({"status": "invalid"})

    entry = db[key]

    # 🔥 ήδη χρησιμοποιημένο
    if entry["used"]:
        return jsonify({"status": "used"})

    # 🔥 πρώτο use
    if not entry["activated"]:
        entry["activated"] = True
        entry["hwid"] = hwid
        entry["expiry"] = int(time.time()) + USE_DURATION

        log(f"✅ Key Activated\nKey: `{key}`\nHWID: `{hwid}`")

        return jsonify({"status": "valid"})

    # 🔒 HWID CHECK
    if entry["hwid"] != hwid:
        log(f"⚠️ HWID MISMATCH\nKey: `{key}`\nTried HWID: `{hwid}`")
        return jsonify({"status": "invalid_hwid"})

    # 🔥 EXPIRE = burn
    if entry["expiry"] and time.time() > entry["expiry"]:
        entry["used"] = True

        log(f"🔥 Key Burned\nKey: `{key}`")

        return jsonify({"status": "expired"})

    return jsonify({"status": "valid"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
