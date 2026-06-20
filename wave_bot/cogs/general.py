import discord
from discord import app_commands
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Checks the bot's latency.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'🏓 Pong! {round(self.bot.latency * 1000)}ms')

    @app_commands.command(name="info", description="Displays information about the bot.")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✨ Wave Bot Info",
            description="A premium music bot built with `discord.py` and `Wavelink` (Lavalink integration).",
            color=discord.Color.blue()
        )
        embed.add_field(name="🛠️ Developer", value="Harsh", inline=True)
        embed.add_field(name="🐍 Python Version", value="3.14+", inline=True)
        embed.add_field(name="🤖 discord.py Version", value=discord.__version__, inline=True)
        embed.set_footer(text="Designed for premium audio streaming")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Displays all available commands and how to use them.")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎵 Wave Music Bot - Command Directory",
            description="Use the slash commands (`/`) below to control playback and interact with the bot.",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎧 Music Control",
            value=(
                "**`/play <query>`** - Plays a song or adds it to the queue (YouTube/SoundCloud search)\n"
                "**`/queue`** - View the list of upcoming songs in the queue\n"
                "**`/skip`** - Skip the current song playing\n"
                "**`/previous`** - Play the previous song in history\n"
                "**`/next`** - Skip the current song (alias to skip)\n"
                "**`/stop`** - Stop audio playback and clear the queue\n"
                "**`/leave`** - Disconnect the bot from the voice channel"
            ),
            inline=False
        )

        embed.add_field(
            name="⚙️ Utilities",
            value=(
                "**`/help`** - Shows this stylized command guide\n"
                "**`/ping`** - Measure the bot connection latency\n"
                "**`/info`** - View bot development details and versions"
            ),
            inline=False
        )

        embed.set_footer(text="Keep it vibing! Powered by Wavelink & Lavalink Node")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
