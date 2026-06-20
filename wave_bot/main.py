# pyrefly: ignore [missing-import]
import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Bot Intents
intents = discord.Intents.default()
intents.message_content = True  # Required for accessing message content
intents.voice_states = True     # Required for voice channel events

# Bot Prefix and Initialization
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('------')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s) globally.")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

# Run the bot
async def main():
    async with bot:
        await bot.load_extension("cogs.music")
        await bot.load_extension("cogs.security")
        await bot.load_extension("cogs.general")
        await bot.start(os.getenv("DISCORD_TOKEN"))

import asyncio
asyncio.run(main())
