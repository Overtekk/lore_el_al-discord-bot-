from discord.ext import commands
import random


class Reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ids = getattr(bot, "ids", {})

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        m = message.content.lower()
        reac = message.add_reaction

        if "mouette" in m:
            await reac("<:CoolSeagull:1462899121848451134>")
        if "python" in m:
            await reac("🐍")
        if "#pokedle" in m:
            await reac("👏")
        if "tg" in m:
            await reac("😵")
        if "lore" in m:
            await reac("✍")
        if "cafe boosting" in m:
            await reac("☕")
        if "remy" in m:
            await reac("🐀")
        if "coin" in m:
            await reac("🦆")
        if "manu" in m:
            await reac("👨‍🦳")
        if "bebou" in m:
            await reac("🤮")
        if "42" in m:
            await reac("⌨️")
        if "goat" in m:
            await reac("🐐")

        if message.author.id == self.ids.get("RANKOST"):
            if random.randint(1, 20) == 10:
                await reac("🖕")
        if message.author.id == self.ids.get("MEL"):
            if random.randint(1, 20) == 10:
                await reac("🐇")

async def setup(bot):
    await bot.add_cog(Reaction(bot))
