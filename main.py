import discord
from discord.ext import commands
import os
import json
from flask import Flask
from threading import Thread

# ========== Keep Alive Web Server ==========
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ========== Bot Setup ==========
intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

TRIGGER_CHANNEL_ID = int(os.getenv("TRIGGER_ID"))
VOICE_CATEGORY_ID = int(os.getenv("CATEGORY_ID"))
DATA_FILE = "vc_data.json"

# ========== Load & Save Data ==========
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

user_temp_channels = load_data()

# ========== Events ==========
@bot.event
async def on_ready():
    print(f"Bot aktif sebagai {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.id == TRIGGER_CHANNEL_ID:
        guild = after.channel.guild
        category = discord.utils.get(guild.categories, id=VOICE_CATEGORY_ID)

        new_channel = await guild.create_voice_channel(
            name=f"{member.display_name}",
            category=category
        )
        await member.move_to(new_channel)

        user_temp_channels[str(member.id)] = {
            "channel_id": new_channel.id,
            "owner_id": member.id,
            "channel_name": new_channel.name
        }
        save_data(user_temp_channels)

    if before.channel:
        for uid, info in list(user_temp_channels.items()):
            if info["channel_id"] == before.channel.id:
                if len(before.channel.members) == 0:
                    await before.channel.delete()
                    del user_temp_channels[uid]
                    save_data(user_temp_channels)
                    break

# ========== Run ==========
keep_alive()
bot.run(os.getenv("TOKEN"))
