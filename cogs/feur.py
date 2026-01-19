import discord
import random
import re
from discord.ext import commands


class Feur(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_chaos_id = 1452288648568504351

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        chaos_channel = self.bot.get_channel(self.channel_chaos_id)
        message_feur_list = ["feur", "feur !", "feur :)", "feuuuur", "feur..", "c'est feur", "**feur**", "# feur", "## feur", "### feur", "`feur`", "*feur*", "||feur||", ":regional_indicator_f: :regional_indicator_e: :regional_indicator_u: :regional_indicator_r:", "~~feur~~", "```for feur in feur do feur```", "double feur", "feur et michon", "c'est ta tete qui est feur", "un feur pour toi", "qu.. feur!", "._. (feur)", "(feur)", "furry", "www.feur.fr", "ruef", "fheure", "ffeeuurree", "remy tg", "f-e--u-r", "fileur", "\\feur\\", "tg et feur", "https://tenor.com/view/feur-theobabac-quoi-gif-24294658", "https://tenor.com/view/feur-gif-23547897", "https://tenor.com/view/quoi-feur-quoi-feur-coiffeur-freaky-versus-gif-25841907", "https://tenor.com/view/feur-quoicoubeh-groundhog-yelling-screaming-gif-8843671686369545947", "https://tenor.com/view/yakalle-laecas-ellen-hopkins-elders-life-gif-6710339651833617604", "https://tenor.com/view/multicort-feur-gif-23304150", "https://tenor.com/view/feur-chat-feur-quoi-feur-gif-3011786818937733079", "https://tenor.com/view/jojo-bizzare-adventure-your-next-line-is-joseph-joestar-feur-gif-2521857813527830171", "https://tenor.com/view/feur-gif-27136381", "https://tenor.com/view/jarvis-feur-gif-27616197", "https://tenor.com/view/feurbot-feur-wizard-spell-sorcier-gif-15154639426955749898"]
        message_quoi_list = ["feur", "Tu as le droit de dire quoi tu sais :)", "Dis quoi si ça te chante !"]

        content_lower = message.content.lower()

        if re.search(r'\b(pour)?quoi\W*$', content_lower) or content_lower in [m.lower() for m in message_quoi_list]:
            if isinstance(message.channel, discord.Thread):
                await message.channel.send(random.choice(message_feur_list))
            else:
                await chaos_channel.send(random.choice(message_feur_list))


async def setup(bot):
    await bot.add_cog(Feur(bot))
