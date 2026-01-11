import os
import discord
import random
import re
import database
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands

# Get private token
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Config for permissions
intents = discord.Intents.default()
intents.message_content = True

class MyClient(commands.Bot):
    def __init__(self, intents):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        database.create_tables()
        await self.load_extension("cogs.game")
        await self.tree.sync()

    async def on_ready(self):
        print(f"Bot connected as {self.user}!")

    async def on_message(self, message):

        await self.process_commands(message)
        message_list = ["feur", "feur !", "feur :)", "feuuuur", "feur..", "c'est feur"]

        if message.author is not self.user:
            if re.search(r'\bquoi\W*$', message.content.lower()):
                await message.channel.send(random.choice(message_list))
            if re.search(r'\bpourquoi\W*$', message.content.lower()):
                await message.channel.send(random.choice(message_list))


# Launch the bot
bot = MyClient(intents=intents)
bot.run(token)
