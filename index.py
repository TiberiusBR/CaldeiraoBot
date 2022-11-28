import nextcord
import os
from dotenv import load_dotenv
from nextcord.ext import commands

from helpers.logger import logger
from cogs.music import Music
from cogs.misc import Misc

import asyncio

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def health():
    return {"Health": "Ok!"}

load_dotenv()

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    logger.info('Ready!')

bot.add_cog(Music(bot))
bot.add_cog(Misc(bot))

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(bot.start(os.getenv('BOT_TOKEN')))
    await asyncio.sleep(4) #optional sleep for established connection with discord
    logger.info(f"{bot.user} has connected to Discord!")

if __name__ == "__main__":
    uvicorn.run(app, port=8000)
