import os
import discord
from dotenv import load_dotenv
import random

# Get private token
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Config for permissions
intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Bot connected as {self.user}!")

    async def on_message(self, message):

        message_list = ["feur", "feur !", "feur :)", "feuuuur", "feur..", "c'est feur"]

        if message.author is not self.user:
            if message.content.lower().endswith("quoi"):
                await message.channel.send(random.choice(message_list))


# Launch the bot
bot = MyClient(intents=intents)
bot.run(token)
