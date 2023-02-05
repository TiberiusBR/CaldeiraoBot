import nextcord
import os
from dotenv import load_dotenv
from nextcord.ext import commands

from helpers.logger import logger

from cogs.music import Music
from cogs.misc import Misc
from cogs.chat_gpt import ChatGPT

import wavelink

load_dotenv()

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    logger.info('Ready!')
    bot.loop.create_task(node_connect())


async def node_connect():
    await bot.wait_until_ready()
    await wavelink.NodePool.create_node(bot=bot,
                                           host=str(os.getenv('LAVALINK_HOST')),
                                           port=str(os.getenv('LAVALINK_PORT')),
                                           password=str(os.getenv('LAVALINK_PASSWORD')),
                                           region="brazil")

bot.add_cog(Music(bot))
bot.add_cog(Misc(bot))
bot.add_cog(ChatGPT(bot))

bot.run(os.getenv('BOT_TOKEN'))
