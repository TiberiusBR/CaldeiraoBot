import nextcord
import os
from dotenv import load_dotenv
from nextcord.ext import commands

from helpers.logger import logger
from cogs.music import Music
from cogs.misc import Misc

load_dotenv()

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    logger.info('Ready!')

# @bot.event
# async def on_message(message):
#     print(f'Message from {message.author}: {message.content}')

bot.add_cog(Music(bot))
bot.add_cog(Misc(bot))

bot.run(os.getenv('BOT_TOKEN'))