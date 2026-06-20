import os
import discord
import wavelink
from discord import app_commands
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.node = None
        self.original_messages = {}

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Connects to Lavalink node when the bot is ready."""
        if not wavelink.Pool.nodes:
            lavalink_host = os.getenv("LAVALINK_HOST", "127.0.0.1")
            lavalink_port = os.getenv("LAVALINK_PORT", "2333")
            lavalink_password = os.getenv("LAVALINK_PASSWORD", "youshallnotpass")
            print(f"Music Cog connecting to Host: {lavalink_host}, Port: {lavalink_port}, Password: {lavalink_password}")
            nodes = [wavelink.Node(uri=f"http://{lavalink_host}:{lavalink_port}", password=lavalink_password)]
            await wavelink.Pool.connect(client=self.bot, nodes=nodes)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        print(f'Wavelink Node connected: {payload.node!r} | Resumed: {payload.resumed}')

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
        player = payload.player
        if not player or not player.guild: return

        original_message = self.original_messages.get(player.guild.id)
        if original_message:
            embed = discord.Embed(title="Now Playing", description=f"[{payload.track.title}]({payload.track.uri})")
            await original_message.edit(embed=embed)

    @app_commands.command(name="play", description="Plays a song from YouTube or adds it to the queue.")
    async def play(self, interaction: discord.Interaction, *, query: str):
        """Plays a song from YouTube."""
        await interaction.response.defer()

        # Check user's voice state (using guild voice_states cache as a fallback if interaction.user.voice is None)
        voice_state = interaction.user.voice or interaction.guild.voice_states.get(interaction.user.id)

        if not voice_state or not voice_state.channel:
            return await interaction.followup.send("You must be connected to a voice channel to play music!")

        if not interaction.guild.voice_client:
            vc: wavelink.Player = await voice_state.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = interaction.guild.voice_client

        tracks = await wavelink.Playable.search(query)
        if not tracks:
            return await interaction.followup.send(f'No tracks found for query: {query}')

        track = tracks[0]
        # Keep original message for the on_wavelink_track_start listener
        self.original_messages[interaction.guild_id] = await interaction.original_response()

        if vc.playing or vc.paused:
            await vc.queue.put_wait(track)
            await interaction.followup.send(f'Added **{track.title}** to the queue.')
        else:
            await vc.play(track)
            await interaction.followup.send(f'Now playing: **{track.title}**')

    @app_commands.command(name="stop", description="Stops the current song and clears the queue.")
    async def stop(self, interaction: discord.Interaction):
        """Stops the current song and clears the queue."""
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("I'm not connected to a voice channel.")

        vc: wavelink.Player = interaction.guild.voice_client
        await vc.stop()
        vc.queue.clear()
        await interaction.response.send_message("Stopped playing and cleared the queue.")

    @app_commands.command(name="skip", description="Skips the current song.")
    async def skip(self, interaction: discord.Interaction):
        """Skips the current song."""
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("I'm not connected to a voice channel.")

        vc: wavelink.Player = interaction.guild.voice_client
        if vc.queue.is_empty and not vc.playing:
            return await interaction.response.send_message("No more songs in the queue.")

        await vc.stop()
        await interaction.response.send_message("Skipped the current song.")

    @app_commands.command(name="previous", description="Plays the previous song in the history.")
    async def previous(self, interaction: discord.Interaction):
        """Plays the previous song in the history."""
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("I'm not connected to a voice channel.")

        vc: wavelink.Player = interaction.guild.voice_client
        await interaction.response.defer()

        history_len = len(vc.queue.history)

        if vc.current is not None:
            if history_len < 2:
                return await interaction.followup.send("No previous track in history.")
            
            prev_track = vc.queue.history[-2]
            current_track = vc.current
            
            # Remove current track and previous track from history since they will be played/re-queued
            vc.queue.history.delete(len(vc.queue.history) - 1)
            vc.queue.history.delete(len(vc.queue.history) - 1)

            # Insert current track back to the front of the queue
            vc.queue.put_at(0, current_track)
            
            await vc.play(prev_track)
            await interaction.followup.send(f"⏮️ Playing previous track: **{prev_track.title}**")
        else:
            if history_len < 1:
                return await interaction.followup.send("No previous track in history.")
            
            prev_track = vc.queue.history[-1]
            
            # Remove from history as playing it will add it back
            vc.queue.history.delete(len(vc.queue.history) - 1)
            
            await vc.play(prev_track)
            await interaction.followup.send(f"⏮️ Playing previous track: **{prev_track.title}**")

    @app_commands.command(name="next", description="Plays the next song in the queue (alias to skip).")
    async def next(self, interaction: discord.Interaction):
        """Plays the next song in the queue (alias to skip)."""
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("I'm not connected to a voice channel.")

        vc: wavelink.Player = interaction.guild.voice_client
        if vc.queue.is_empty and not vc.playing:
            return await interaction.response.send_message("No more songs in the queue.")

        await vc.stop()
        await interaction.response.send_message("⏭️ Skipped to the next song.")


    @app_commands.command(name="queue", description="Shows the current song queue.")
    async def queue(self, interaction: discord.Interaction):
        """Shows the current song queue."""
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("I'm not connected to a voice channel.")

        vc: wavelink.Player = interaction.guild.voice_client
        if vc.queue.is_empty:
            return await interaction.response.send_message("The queue is empty.")

        q = vc.queue.copy()
        upcoming = ' '.join(f'**{i+1}.** {t.title}\n' for i, t in enumerate(q))
        embed = discord.Embed(title="Queue", description=upcoming or "Queue is empty.", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leave", description="Disconnects the bot from the voice channel.")
    async def leave(self, interaction: discord.Interaction):
        """Disconnects the bot from the voice channel."""
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("I'm not in a voice channel.")

        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Disconnected from voice channel.")

async def setup(bot):
    await bot.add_cog(Music(bot))
