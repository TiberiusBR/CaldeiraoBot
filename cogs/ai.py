import nextcord
from nextcord.ext import commands
from nextcord import Interaction

import asyncio
from helpers.logger import logger

import openai

import os
class AI(commands.Cog):
    def __init__(self, bot) -> None:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.bot = bot

    @nextcord.slash_command(name="gpt", description="Ask Bill a question!")
    async def gpt(self, interaction: Interaction, prompt: str):
        """Asks OPEN AI, chat gpt a question and try to return the answer."""
        try:
            logger.debug(f"Question from user id {interaction.user.id}: {prompt}")
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
        
    @nextcord.slash_command(name="image",description="Ask Bill to generate a image for you!")
    async def image(self,interaction: Interaction, prompt: str):
        """Asks OPEN AI to generate a image based on a prompt"""
        try:
            logger.debug(f"Prompt from user id {interaction.user.id}: {prompt}")
            await interaction.response.defer()
            embed = nextcord.Embed(title=f"{prompt}", description=f"Imagem pedida por {interaction.user.display_name}")
            response = openai.Image.create(
                prompt=f"{prompt}",
                n=1,
                size="512x512"
            )
            image_url = response['data'][0]['url']
            embed.set_image(image_url)
            await asyncio.sleep(0.1)
            await interaction.send(embed=embed)
        except openai.error.OpenAIError:
            await asyncio.sleep(0.1)
            await interaction.send("Desculpe, mas você pediu algo que não é permitido pelo OpenAI! Tente novamente!")
        except Exception as ex:
            logger.error(f"Error - {ex}")
