import nextcord
from nextcord.ext import commands
from nextcord import Interaction, Message
from datetime import datetime
import pytz
import csv
from helpers.logger import logger

class Misc(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    def parse_row(self, message: Message) -> list:
        author_id = message.author.id
        author_name = message.author.name
        content = message.clean_content.replace(";", " ")
        attach = message.attachments
        attachment = attach[0].proxy_url if len(attach) > 0 else ''
        datet = message.created_at.astimezone(pytz.timezone('America/Bahia')).strftime('%Y-%m-%d %H:%M:%S')
        return [author_id, author_name, content, attachment, datet]

    
    def generate_csv(self, messages: list):
        logger.info("Generating CSV")
        fields = ['user_id','user_name','message','attachment','date']
        data = [self.parse_row(message=msg) for msg in messages]
        with open('data.csv','w+') as f:
            write = csv.writer(f, delimiter=';')
            write.writerow(fields)
            write.writerows(data)
        logger.info("Done!")
        return data
    
    @nextcord.slash_command(name="generate_history", description="Generate", default_member_permissions=8)
    async def generate_history(self, interaction: Interaction):
        channel = interaction.channel
        logger.info("Generating messages.")
        messages = await channel.history(limit=100).flatten()
        logger.info("Finished message collection.")
        data = self.generate_csv(messages)
        print("ok!")