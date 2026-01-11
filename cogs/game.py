import discord
from discord.ext import commands, tasks
from discord import app_commands
import database
import datetime
import random


# Player ID for players on my server
players_id = [
    209661299901202432, # Overtek
    689790526672732172, # Ana
    396014113161216003, # Melkope
    800732451130966088, # Rankost
    227464050177474561, # Sahovo
    228948435259228160, # Astyell
    296298507554521090, # Heretikk
    177835554304557056, # LadyGuilty
    745032303327182939, # Shadox
    303279758941356035  # Neloryx
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

    # Load the core game
    async def cog_load(self):
        print("Loading game module... Veryfing players")

        # Register player in the data base
        for id in players_id:
            database.register_player(id)
            database.add_score(id, 0)
            print(f"{id}: registered")

        print("Loading and verification finished!\n")
        self.game_loop.start()

    # Core loop of the game
    @tasks.loop(minutes=1)
    async def game_loop(self):
        # Define the time and the channel
        h_now = datetime.datetime.now()
        channel = self.bot.get_channel(self.game_channel_id)

        # === Starting the game ===
        if h_now.hour == self.start_hour:
            if self.secret_number is None:
                    await self.start_game_logic()

                    embed = discord.Embed(
                        title="🎲 GuessTheNumber have started!",
                        description=f"Guess the secret number between **{self.min_n}** and **{self.max_n}** included.\nPoints are awarded by the number of players that hasn't played.\nUse /guess 'number' to play\n\nGood luck!",
                        color=discord.Color.blue()
                    )

                    await channel.send(content="@everyone", embed=embed)

        # === Stop the game at 23h59 everyday ===
        if h_now.hour == 23 and h_now.minute == 59:
            if self.secret_number is not None:

                embed = discord.Embed(
                    title="🌙 GuessTheNumber is finished!",
                    description=f"No one find the number today 😪.\nIt was **{self.secret_number}**.",
                    color=discord.Color.dark_grey()
                )
                await channel.send(embed=embed)

                self.secret_number = None
                self.start_hour = random.randint(10, 19)

    async def start_game_logic(self):
        self.players = len(players_id)
        self.max_n = random.randint(10, 20)
        self.secret_number = random.randint(self.min_n, self.max_n)
        database.reset_daily_attempts()

    @app_commands.command(name="guess", description="Try to guess the number of the day!")
    async def guess(self, interaction: discord.Interaction, number: int):
        # === Check if player exist ===
        if interaction.user.id not in players_id:
            return

        # === Check if secret number exist ===
        if self.secret_number is None:

            embed_not_open = discord.Embed(
                title="❌ NOT STARTED",
                description="Game is not open.",
                color=discord.Color.red()
            )

            await interaction.response.send_message(embed=embed_not_open, ephemeral=True)
            return

        # === Check if player have already played ===
        if database.has_played_today(interaction.user.id):
            embed_played = discord.Embed(
                title="❌ ALREADY PLAYED",
                description="You already have played today.",
                color=discord.Color.red()
            )

            await interaction.response.send_message(embed=embed_played, ephemeral=True)
            return

        # === Check if player guess have the right number ===
        if number == self.secret_number:
            database.add_score(interaction.user.id, self.players)
            self.secret_number = None

            embed_win = discord.Embed(
                title="🎉 VICTORY!",
                description=f"{interaction.user.mention} find the mystery number: (**{number}**) !\n**{self.players} point earned!**.\nGame have ended.",
                color=discord.Color.gold()
            )

            await interaction.response.send_message(embed=embed_win)
            return

        # === Else, mark player as played ===
        else:
            database.mark_as_played(interaction.user.id)
            self.players -= 1

            description_txt = "It's not the right number.\nYou failed for today."
            show_hint = random.choice([True, False])
            if show_hint:
                if self.secret_number > number:
                    hint = "\n\n👻 **Hint:** The number is **HIGHER**⬆️!"
                else:
                    hint = "\n\n👻 **Hint:** The number is **LOWER**⬇️!"
                description_txt += hint

            embed_loose = discord.Embed(
                title="❌ WRONG",
                description = description_txt,
                color=discord.Color.red()
            )

            await interaction.response.send_message(embed=embed_loose)

            # === End the game if everyone have played===
            if self.players == 0:
                channel = self.bot.get_channel(self.game_channel_id)

                embed_end = discord.Embed(
                    title="⛔ GAME OVER",
                    description=f"Everyone failed for today.\nThe number was: **{self.secret_number}**.\nGame have ended.",
                    color=discord.Color.dark_red()
                )

                await channel.send(embed=embed_end)

                self.start_hour = random.randint(10, 19)
                self.secret_number = None
                return
            return


    @app_commands.command(name="leaderboard", description="Show the top players")
    @app_commands.checks.cooldown(1, 60.0)
    async def leaderboard(self, interaction: discord.Interaction):
        data = database.get_leaderboard()

        msg_txt = ""
        for rank, (user_id, score) in enumerate(data, start=1):
            msg_txt += f"{rank}. <@{user_id}> : **{score}** points\n"

        embed = discord.Embed(title="🏆 Leaderboard", description=msg_txt, color=discord.Color.gold())
        await interaction.response.send_message(embed=embed)

    @leaderboard.error
    async def on_leaderboard_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"⏳ Please wait {int(error.retry_after)} seconds before using this command again.", ephemeral=True)


    @app_commands.command(name="start", description="🔴 ADMIN: Force the start of the game")
    async def start(self, interaction: discord.Interaction):
        if interaction.user.id != players_id[0]:
            await interaction.response.send_message("⛔ You can't do this", ephemeral=True)
            return

        if self.secret_number is not None:
            await interaction.response.send_message("Game already started", ephemeral=True)
            return

        await self.start_game_logic()
        await interaction.response.send_message("✅ Game launched", ephemeral=True)
        channel = self.bot.get_channel(self.game_channel_id)
        embed = discord.Embed(
            title="🎲 GuessTheNumber have started! (Admin launch)",
            description=f"Guess the secret number between **{self.min_n}** and **{self.max_n}** included.\nPoints are awarded by the number of players that hasn't played.\n\nGood luck!",
            color=discord.Color.blue()
        )
        await channel.send(content="@everyone", embed=embed)


async def setup(bot):
    await bot.add_cog(GuessNumber(bot))


