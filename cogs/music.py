from nextcord.ext import commands
from helpers.ytdl import YTDLSource

class Music(commands.Cog):
    def _init_(self,bot):
        self.bot = bot
        self.queues = {}
    
    def check_queue(self,ctx, id):
        if self.queues[id] != []:
            voice = ctx.guild.voice_client
            source = self.queues[id].pop(0)
            player = voice.play(source)
    
    @commands.command()
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        if channel is None:
            await ctx.send(f"You aren't connected to any channel.")

        await channel.connect()
    
    @commands.command()
    async def play(self, ctx, *, url):
        """Streams from a URL (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=ctx.bot.loop, stream=True)
            ctx.voice_client.play(
                player, after=lambda x=None: self.check_queue(ctx,ctx.message.guild.id)
            )

        await ctx.send(f"Now playing: {player.title}")
    
    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()
    
    @commands.command()
    async def queue(self,ctx, *, url):
        """Adds a youtube video to the queue."""
        
        player = await YTDLSource.from_url(url, loop=ctx.bot.loop, stream=True)

        guild_id = ctx.message.guild.id

        if guild_id in self.queues:
            self.queues[guild_id].append(player)
        else:
            self.queues[guild_id] = [player]
        
        return ctx.send(f"Added {player.title} to queue.")


    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()
