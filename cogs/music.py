import nextcord
from nextcord.ext import commands
from nextcord import Interaction

import datetime

import wavelink

from helpers.logger import logger


class CustomPlayer(wavelink.Player):

    def __init__(self):
        super().__init__()
        self.queue = wavelink.Queue()


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.info_queues = {}

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: CustomPlayer, track: wavelink.Track, reason):
        if not player.queue.is_empty:
            next_track = player.queue.get()
            await player.play(next_track)

    def parse_time(self, duration: float):
        return str(datetime.timedelta(seconds=duration))

    async def ensure_voice(self, interaction: Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            if interaction.user.voice:
                voice_client: CustomPlayer = await interaction.user.voice.channel.connect(cls=CustomPlayer())
            else:
                await interaction.send("You are not connected to a voice channel.")
                raise commands.CommandError(
                    "Author not connected to a voice channel.")
        return voice_client

    @nextcord.slash_command(name="join", description="Joins current user voice channel.")
    async def join(self, interaction: Interaction):
        voice_channel = interaction.user.voice.channel
        await self.ensure_voice(interaction)
        await interaction.send(f"Connected to channel {voice_channel.name}")

    @nextcord.slash_command(name="play", description="Play a video from a youtube URL or query.")
    async def play(self, interaction: Interaction, search: str):
        """Streams from a URL (same as yt, but doesn't predownload)"""
        try:
            voice_client = await self.ensure_voice(interaction)
            embed = None
            if "playlist" in search:
                search = await wavelink.YouTubePlaylist.search(query=search)
                tracks: list = search.tracks
                track_amount = len(tracks)
                await voice_client.play(tracks.pop(0))
                for track in tracks:
                    voice_client.queue.put(track)
                embed = nextcord.Embed(title="Playlist enqueued!",
                                       description=f"Added playlist **{search.name}**, with **{track_amount}** tracks to queue!")
            else:
                if "&" in search and "youtube" in search:
                    search = search.split("&")[0]
                search = await wavelink.YouTubeTrack.search(query=search, return_first=True)
                if voice_client.is_playing():
                    voice_client.queue.put(search)
                    embed = nextcord.Embed(title=search.title,
                                           url=search.uri,
                                           description=f"Added **{search.title}** to queue!")
                else:
                    await voice_client.play(search)
                    embed = nextcord.Embed(title=search.title,
                                           url=search.uri,
                                           description=f"Playing **{search.title}**!")
            await interaction.send(embed=embed)
        except Exception as ex:
            logger.error(f"A exception ocurred: {ex}")
            await interaction.followup.send("The video couldn't be played. Try again.")

    @nextcord.slash_command(name="queue", description="Retrieve all songs currently on the server queue.")
    async def queue(self, interaction: Interaction):
        """Retrieve songs from queue"""
        empty_msg = ""
        message = f"All songs currently in queue for **{interaction.guild.name}**: \n >>> "
        try:
            try:
                queue_obj = interaction.guild.voice_client.queue
                queue_size = queue_obj.count
                queue = queue_obj._queue
                queue_messages = []
                if queue_size > 0:
                    for idx, song in enumerate(queue):
                        if idx <= 9:
                            queue_messages.append(f"**{song.title}** - `({self.parse_time(song.duration)})`\n")
                        else:
                            empty_msg = f"And more {queue_size - idx} songs in queue!"
                            break
                else:
                    message += "**There are currently no songs in queue.**"
                message += "".join(queue_messages)
                message += empty_msg
            except:
                logger.error(f"A exception ocurred: {ex}")
            await interaction.send(message)
        except Exception as ex:
            logger.error(f"A exception ocurred: {ex}")
            await interaction.followup.send("Could not check queue. Try again.")

    @nextcord.slash_command(name="stop", description="Disconnect bot from voice channel and clear queue, if there's one.")
    async def stop(self, interaction: Interaction):
        """Stops and disconnects the bot from voice"""
        voice_client = interaction.guild.voice_client
        queue = voice_client.queue
        await voice_client.stop()
        voice_client.cleanup()
        await voice_client.disconnect()
        queue.clear()
        await interaction.send("Queue cleared and disconnected from voice channel.")

    @nextcord.slash_command(name="skip", description="Plays the next song in queue, if there's any.")
    async def skip(self, interaction: Interaction):
        """Skips current song."""
        voice_client = interaction.guild.voice_client
        if voice_client:
            if not voice_client.is_playing():
                voice_client = interaction.guild.voice_client
                video_title = voice_client.source.title
                voice_client.stop()
                await interaction.send(f"Skipping {video_title}")
            if voice_client.queue.is_empty:
                await voice_client.stop()
                await interaction.send("There's no songs left in the queue. Stopping current song.")

            await voice_client.seek(voice_client.track.length * 1000)
            if voice_client.is_paused():
                await voice_client.resume()
        else:
            await interaction.send("Not connected to any voice channel.")