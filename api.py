import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask, request, jsonify
import threading
import secrets
import json
import time
import requests

TOKEN = "MTQ2OTgxMDI3NzM5MzUwMjQ2NQ.GwYEuL.TbcQx7xZ_lMhA6k_mlg2YaP1o259vLMu7NrzBc"
GUILD_ID = 1287320963545038942
ALLOWED_ROLE_IDS = [1335193487267860581]

DB_FILE = "keys.json"

def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ================= API =================
app = Flask(__name__)

@app.route("/gen", methods=["POST"])
def gen():
    key = secrets.token_hex(16)
    db = load_db()

    db[key] = {"used": False, "expiry": None}
    save_db(db)

    return jsonify({"key": key})

@app.route("/check", methods=["POST"])
def check():
    data = request.json
    key = data.get("key")

    db = load_db()

    if key not in db:
        return jsonify({"status": "invalid"})

    entry = db[key]

    if not entry["used"]:
        entry["used"] = True
        entry["expiry"] = int(time.time()) + 300
        save_db(db)
        return jsonify({"status": "valid"})

    if entry["expiry"] and time.time() > entry["expiry"]:
        return jsonify({"status": "expired"})

    return jsonify({"status": "valid"})

# ================= BOT =================
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def is_allowed(interaction):
    return any(role.id in ALLOWED_ROLE_IDS for role in interaction.user.roles)

@bot.tree.command(name="genkey")
async def genkey(interaction: discord.Interaction):

    if not is_allowed(interaction):
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    r = requests.post("http://127.0.0.1:5000/gen")
    key = r.json()["key"]

    msg = (
        "Link to download the scanner : https://limewire.com/d/6Loza#3X1fAeV7rg\n"
        f"Key: {key}\n"
        "Scan and check"
    )

    await interaction.user.send(msg)
    await interaction.response.send_message("✅ Check your DM", ephemeral=True)

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    print("Bot Ready")

def run_api():
    app.run(host="0.0.0.0", port=5000)

threading.Thread(target=run_api).start()

bot.run(TOKEN)
