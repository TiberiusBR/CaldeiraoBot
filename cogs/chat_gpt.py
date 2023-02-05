import nextcord
from nextcord.ext import commands
from nextcord import Interaction

import asyncio
from helpers.logger import logger

import openai


class ChatGPT(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @nextcord.slash_command(name="gpt", description="Ask Chat-GPT a question!")
    async def gpt(self, interaction: Interaction, prompt: str):
        """Asks OPEN AI, chat gpt a question and try to return the answer."""
        try:
            logger.info(f"Question from user id {interaction.user.id}: {prompt}")
            await interaction.response.defer()
            embed = nextcord.Embed(title=f"Pergunta de {interaction.user.display_name}", description=prompt)
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=0.9,
                max_tokens=300,
                frequency_penalty=0.0,
                presence_penalty=0.6
            )
            embed.add_field(name="Resposta:", value=response.choices[0].text)
            await asyncio.sleep(0.1)
            await interaction.send(embed=embed)
        except Exception as ex:
            logger.error(f"Error - {ex}")
        
