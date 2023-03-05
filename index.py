import nextcord
import os
from dotenv import load_dotenv
from nextcord.ext import commands

from helpers.logger import logger

from cogs.music import Music
from cogs.misc import Misc
from cogs.ai import AI

import wavelink
import time

load_dotenv()

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    logger.info('Bot Ready! Creating lavalink node...')
    bot.loop.create_task(node_connect())


async def node_connect():
    await bot.wait_until_ready()
    count = 0
    while count < 10:
        node = await wavelink.NodePool.create_node(bot=bot,
                                                host=str(os.getenv('LAVALINK_HOST')),
                                                port=str(os.getenv('LAVALINK_PORT')),
                                                password=str(os.getenv('LAVALINK_PASSWORD')),
                                                region="brazil") 
        if node._websocket.websocket != None:
            logger.info("Node Connected!")
            break
        logger.error("Could not connect to wavelink. Trying again in 10 seconds.")
        count += 1
        time.sleep(10)
    

bot.add_cog(Music(bot))
bot.add_cog(Misc(bot))
bot.add_cog(AI(bot))

bot.run(os.getenv('BOT_TOKEN'))
