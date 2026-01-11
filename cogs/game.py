import discord
from discord.ext import commands, tasks
from discord import app_commands
import database
import datetime
import random


players_id = [
    209661299901202432, # Overtek
    689790526672732172, # Ana
    396014113161216003, # Melkope
    800732451130966088, # Rankost
    227464050177474561, # Sahovo
    228948435259228160, # Astyell
    296298507554521090, # Heretikk
    177835554304557056, # LadyGuilty
    745032303327182939  # Shadox
]


class GuessNumber(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.secret_number = None
        self.min_n = 1
        self.max_n = 20
        self.players = 0
        self.game_channel_id = 1452288714045919374
        self.start_hour = random.randint(10, 19)

    async def cog_load(self):
        print("Loading game module... Veryfing players")
        for id in players_id:
            database.register_player(id)
            database.add_score(id, 0)
            print(f"{id}: registered")
        print("Loading and verification finished!\n")
        self.game_loop.start()

    @tasks.loop(minutes=1)
    async def game_loop(self):
        h_now = datetime.datetime.now()
        channel = self.bot.get_channel(self.game_channel_id)

        if h_now.hour == self.start_hour:
            if self.secret_number is None:
                    self.players = len(players_id)
                    self.max_n = random.randint(10, 20)
                    self.secret_number = random.randint(self.min_n, self.max_n)
                    database.reset_daily_attempts()
                    await channel.send(f"@everyone \n Guess the number have started. Try to guess the number betweeb {self.min_n} and {self.max_n} included! Good luck.")

        if h_now.hour == 23 and h_now.minute == 59:
            if self.secret_number is not None:
                await channel.send(f"Game finished for today. No one find the number {self.secret_number}. Too bad :()")
                self.secret_number = None
                self.start_hour = random.randint(10, 19)

    @app_commands.command(name="guess", description="Try to guess the number of the day!")
    async def guess(self, interaction: discord.Interaction, number: int):
        # Check if player exist
        if interaction.user.id not in players_id:
            return

        # Check if secret number exist
        if self.secret_number is None:
            await interaction.response.send_message("Game hasn't started.")
            return

        # Check if player have already played
        if database.has_played_today(interaction.user.id):
            await interaction.response.send_message("You already played. Try again tomorrow")
            return

        # Check if player guess is the right number
        if number == self.secret_number:
            database.add_score(interaction.user.id, 1)
            self.secret_number = None
            await interaction.response.send_message(f"🎉 {interaction.user.mention} have found the number. Congratulation!")
            return

        else:
            database.mark_as_played(interaction.user.id)
            await interaction.response.send_message("Wrong.")
            self.players -= 1

            # End the game if everyone have played
            if self.players == 0:
                channel = self.bot.get_channel(self.game_channel_id)
                await channel.send(f"Game finished for today. No one find the number {self.secret_number}. Too bad :()")
                self.start_hour = random.randint(10, 19)
                self.secret_number = None
                return
            return

    @app_commands.command(name="leaderboard", description="Show the top players")
    async def leaderboard(self, interaction: discord.Interaction):
        data = database.get_leaderboard()

        msg_txt = ""
        for rank, (user_id, score) in enumerate(data, start=1):
            msg_txt += f"{rank}. <@{user_id}> : **{score}** points\n"

        embed = discord.Embed(title="🏆 Leaderboard", description=msg_txt, color=discord.Color.gold())
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(GuessNumber(bot))


