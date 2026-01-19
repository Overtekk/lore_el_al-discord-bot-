#!/usr/bin/env python

import os
import discord
import database
import json
from dotenv import load_dotenv
from discord.ext import commands

# Get private token
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Config for permissions
intents = discord.Intents.default()
intents.message_content = True

# Main class
class MyClient(commands.Bot):
    def __init__(self, intents):
        super().__init__(command_prefix="!", intents=intents)

        if os.path.exists("discord_id.json"):
            with open("discord_id.json", "r") as file:
                self.ids = json.load(file)
        else:
            print("Error: 'discord_id.json' missing")
            self.ids = {}

    async def setup_hook(self):
        await self.load_extension("cogs.feur")
        print("Module feur loaded!")
        await self.load_extension("cogs.reaction")
        print("Module reaction loaded!")
        database.create_tables()
        await self.load_extension("cogs.game")
        print("Module GuessTheNumber loaded!")
        await self.tree.sync()

    async def on_ready(self):
        print(f"Bot connected as {self.user}!")

# Launch the bot
bot = MyClient(intents=intents)
bot.run(token)
