import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from helpers.ytdl import YTDLSource

import asyncio
from helpers.logger import logger

class Music(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.queues = {}
    
    def check_queue(self,voice_client, guild_id: int):
        if self.queues[guild_id] != []:
            voice = voice_client
            source = self.queues[guild_id].pop(0)
            player = voice.play(source)
            logger.info(f"Current song for guild {guild_id}: {source.title}")
    
    def clear_queue(self, guild_id):
        if guild_id in self.queues:
            self.queues[guild_id].clear()
            logger.info(f"Queue for {guild_id} cleared.")

    async def add_to_queue(self, interaction: Interaction, url: str):
        """Adds a youtube video to the queue."""
        
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        guild_id = interaction.guild_id
        if guild_id in self.queues:
            self.queues[guild_id].append(player)
        else:
            self.queues[guild_id] = [player]
        return await interaction.send(f"Added {player.title} to queue.")

    ##@play.before_invoke()
    async def ensure_voice(self, interaction: Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            if interaction.user.voice:
                voice_client = await interaction.user.voice.channel.connect()
            else:
                await interaction.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        return voice_client
    
    @nextcord.slash_command(name="join",description="Joins current user voice channel.")
    async def join(self, interaction: Interaction):
        voice_channel = interaction.user.voice.channel
        if voice_channel is None:
            await interaction.send(f"You aren't connected to any channel.")

        await voice_channel.connect()
        await interaction.send(f"Connected to channel {voice_channel.name}")
    
    @nextcord.slash_command(name="play",description="Play a video from a youtube URL.")
    async def play(self, interaction: Interaction, url):
        """Streams from a URL (same as yt, but doesn't predownload)"""
        try:
            await interaction.response.defer()
            voice_client = await self.ensure_voice(interaction)
            if voice_client.is_playing():
                return await self.add_to_queue(interaction,url)
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            video_title = player.title
            voice_client.play(
                player, after=lambda x=None: self.check_queue(voice_client,interaction.guild.id)
            )

            await asyncio.sleep(0.1)
            await interaction.followup.send(f"Now playing: {video_title}")
        except Exception as ex:
            logger.error(f"A exception ocurred: {ex.message}")
            await interaction.followup.send("The video couldn't be played. Try again.")
    
    @nextcord.slash_command(name="stop", description="Disconnect bot from voice channel and clear queue, if there's one.")
    async def stop(self, interaction: Interaction):
        """Stops and disconnects the bot from voice"""
        voice_client = interaction.guild.voice_client
        self.clear_queue(interaction.guild_id)
        voice_client.cleanup()
        await voice_client.disconnect()
    
    @nextcord.slash_command(name="skip", description="Plays the next song in queue, if there's any.")
    async def skip(self, interaction: Interaction):
        """Skips current song."""
        voice_protocol = interaction.guild.voice_client
        if voice_protocol.is_playing():
            voice_client = interaction.guild.voice_client
            video_title = voice_client.source.title
            voice_client.stop()
            await interaction.send(f"Skipping {video_title}")
        else:
            await interaction.send("There's no songs left in the queue.")
