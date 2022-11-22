import nextcord
import os
import logging
from dotenv import load_dotenv
from nextcord.ext import commands

from cogs.music import Music

load_dotenv()

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

TESTING_GUILD_ID = 999453445843062874

# @bot.event
# async def on_message(message):
#     print(f'Message from {message.author}: {message.content}')

bot.add_cog(Music(bot))

bot.run(os.getenv('BOT_TOKEN'))