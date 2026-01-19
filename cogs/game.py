from typing import Union
import discord
from discord.ext import commands, tasks
from discord import app_commands
import database
import datetime
import random


class GuessNumber(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ids = getattr(bot, "ids", {})
        self.secret_number = None
        self.min_n = 1
        self.max_n = 20
        self.points_pool = 0
        self.start_hour = random.randint(9, 19)
        self.start_min = random.randint(1, 59)

    # Load the core game
    async def cog_load(self):
        self.game_loop.start()

    # Core loop of the game
    @tasks.loop(minutes=1)
    async def game_loop(self):
        # Define the time and the channel
        h_now = datetime.datetime.now()
        game_channel_id = self.ids.get("GAME_CHANNEL")
        if not game_channel_id:
            return
        channel = self.bot.get_channel(game_channel_id)

        # === Starting the game ===
        if h_now.hour == self.start_hour and h_now.minute == self.start_min:
            if self.secret_number is None:
                await self.start_game_logic()

                if channel:
                    embed = discord.Embed(
                        title="🎲 GuessTheNumber have started!",
                        description=f"Guess the secret number between **{self.min_n}** and **{self.max_n}** included.\nPoints are awarded by the number of players that hasn't played.\nUse /guess 'number' to play\n\nGood luck!",
                        color=discord.Color.blue()
                    )
                    await channel.send(embed=embed)

        # === Stop the game at 23h59 everyday ===
        if h_now.hour == 23 and h_now.minute == 59:
            if self.secret_number is not None:
                if channel:
                    embed = discord.Embed(
                        title="🌙 GuessTheNumber is finished!",
                        description=f"No one find the number today 😪.\nIt was **{self.secret_number}**.",
                        color=discord.Color.dark_grey()
                    )
                    await channel.send(embed=embed)

                self.secret_number = None
                self.start_hour = random.randint(9, 19)
                self.start_min = random.randint(0, 59)

    async def start_game_logic(self):
        database.reset_daily_attempts()

        self.max_n = random.randint(10, 20)
        self.secret_number = random.randint(self.min_n, self.max_n)

        total_players = database.count_remaining_players()
        self.points_pool = total_players if total_players > 0 else 5

    @app_commands.command(name="guess", description="Try to guess the number of the day!")
    async def guess(self, interaction: discord.Interaction, number: int):

        # === Check if secret number exist ===
        if self.secret_number is None:
            embed_not_open = discord.Embed(
                title="❌ NOT STARTED",
                description="Game is not open yet.",
                color=discord.Color.red()
            )

            await interaction.response.send_message(embed=embed_not_open, ephemeral=True)
            return

        # === Check if player have already played ===
        if database.check_player_status(interaction.user.id):
            embed_played = discord.Embed(
                title="❌ ALREADY PLAYED",
                description="You already have played today.",
                color=discord.Color.red()
            )

            await interaction.response.send_message(embed=embed_played, ephemeral=True)
            return

        # === Check if player guess have the right number ===
        if number == self.secret_number:
            database.add_score(interaction.user.id, self.points_pool)

            secret = self.secret_number
            self.secret_number = None
            self.start_hour = random.randint(10, 19)
            self.start_min = random.randint(0, 59)

            embed_win = discord.Embed(
                title="🎉 VICTORY!",
                description=f"{interaction.user.mention} find the mystery number: (**{secret}**) !\n**{self.points_pool} point earned!**.\nGame have ended.",
                color=discord.Color.gold()
            )
            await interaction.response.send_message(embed=embed_win)

        # === Else, mark player as played ===
        else:
            database.mark_as_played(interaction.user.id)

            if self.points_pool > 1:
                self.points_pool -= 1

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
            remaining = database.count_remaining_players()
            if remaining == 0:
                game_channel_id = self.ids.get("GAME_CHANNEL")
                if game_channel_id:
                    channel = self.bot.get_channel(game_channel_id)
                    embed_end = discord.Embed(
                        title="⛔ GAME OVER",
                        description=f"Everyone failed for today.\nThe number was: **{self.secret_number}**.\nGame have ended.",
                        color=discord.Color.dark_red()
                    )
                    await channel.send(embed=embed_end)

                self.secret_number = None
                self.start_hour = random.randint(10, 19)
                self.start_min = random.randint(0, 59)


    @app_commands.command(name="leaderboard", description="Show the top players")
    @app_commands.checks.cooldown(1, 10.0)
    async def leaderboard(self, interaction: discord.Interaction):
        data = database.get_leaderboard()

        msg_txt = ""
        for rank, (user_id, score) in enumerate(data, start=1):
            msg_txt += f"{rank}. <@{user_id}> : **{score}** points\n"
        if not msg_txt:
            msg_txt = "No scores yet."

        embed = discord.Embed(title="🏆 Leaderboard", description=msg_txt, color=discord.Color.gold())
        await interaction.response.send_message(embed=embed)


    @leaderboard.error
    async def on_leaderboard_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"⏳ Please wait {int(error.retry_after)} seconds before using this command again.", ephemeral=True)


    # ======================================= #
    #              ADMIN                      #
    # ======================================= #

    @commands.command(name="guessfstart")
    async def force_start(self, ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if ctx.author.id != self.ids.get("OVERTEK"):
            return

        if self.secret_number is not None:
            await ctx.send("Can't do this!", delete_after=5)
            return

        await self.start_game_logic()
        embed = discord.Embed(
            title="🎲 GuessTheNumber have started! (Admin)",
            description=f"Guess the secret number between **{self.min_n}** and **{self.max_n}** included.\nPoints are awarded by the number of players that hasn't played.\nUse /guess 'number' to play\n\nGood luck!",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)


    @commands.command(name="guessfstop")
    async def force_stop(self, ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if ctx.author.id != self.ids.get("OVERTEK"):
            return

        if self.secret_number is None:
            await ctx.send("Can't do this!", delete_after=5)
            return

        revelation = self.secret_number
        self.secret_number = None
        await ctx.send(f"🛑 **Game stopped by administrator.**\nThe secret number was : **{revelation}**.")


    @commands.command(name="addpoints")
    async def manage_points(self, ctx, target: Union[discord.Member, discord.User], amount: int):
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if ctx.author.id != self.ids.get("OVERTEK"):
            return

        database.check_player_status(target.id)
        database.add_score(target.id, amount)

        action = "added to" if amount > 0 else "removed to"
        await ctx.send(f"✅ **{abs(amount)}** points have been {action} **{target.display_name}**.", delete_after=5)

async def setup(bot):
    await bot.add_cog(GuessNumber(bot))


