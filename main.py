import discord
from discord.ext import commands
from keep_alive import keep_alive
import os
import time

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

TRIGGER_ID = int(os.getenv("TRIGGER_ID"))
CATEGORY_ID = int(os.getenv("CATEGORY_ID"))

@bot.event
async def on_ready():
    print(f"Bot is ready as {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.id == TRIGGER_ID:
        guild = member.guild
        category = discord.utils.get(guild.categories, id=CATEGORY_ID)
        channel = await guild.create_voice_channel(name=f"{member.name}'s room", category=category)
        await member.move_to(channel)

        def check(x, y, z): return len(channel.members) == 0
        await bot.wait_for('voice_state_update', check=check)
        await channel.delete()

keep_alive()

while True:
    try:
        bot.run(os.getenv("TOKEN"))
    except Exception as e:
        print(f"Bot error: {e}")
        time.sleep(5)
