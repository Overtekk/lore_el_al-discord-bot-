from discord.ext import commands
from discord import app_commands
import discord
import random
import asyncio
from datetime import timedelta


class Sus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sus", description="Check if your sus. Watch out")
    @app_commands.checks.cooldown(1, 800.0)
    async def sus_command(self, interaction: discord.Interaction):

        embed_loading = discord.Embed(
            title="🕵️ Checking suspicion levels...",
            description="Analyzing behavior...",
            color=discord.Color.light_grey()
        )
        await interaction.response.send_message(embed=embed_loading)

        await asyncio.sleep(5)

        sus = random.randint(0, 12)
        sus2 = random.randint(0, 12)


        if sus == sus2:
            await interaction.followup.send("https://tenor.com/view/among-us-sus-videogame-gameplay-multiplayer-gif-19098192")
            try:
                await interaction.user.timeout(timedelta(seconds=60), reason="You are so sus bro...")

                embed_sus = discord.Embed(
                    title="🚨 IMPOSTOR DETECTED 🚨",
                    description=f"{interaction.user.mention} was **SUS**!\nEjected for **60 seconds**.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed_sus)

            except discord.Forbidden:
                await interaction.followup.send("⚠️ You are SUS, but I don't have permission to eject you...")
                space_art = f"""```
                .      　。　　　　•　    　ﾟ　　。
                　　.　　　.　　　  　　.　　　　　。
                　　.　　　　　　*　　.　　　　
                　{interaction.user.display_name} was An Impostor.
                　 　　。　　 　　　　ﾟ　　　.　
                　　　.　　　  　　.　　　　　。
                ```"""
                await interaction.followup.send(space_art)

        else:
            embed_safe = discord.Embed(
                title="✅ Crewmate Confirmed",
                description="Not sus... for now",
                color=discord.Color.green()
            )
            await interaction.edit_original_response(embed=embed_safe)

    @sus_command.error
    async def on_sus_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏳ Please wait **{int(error.retry_after // 60)} minutes** and **{int(error.retry_after % 60)} seconds** before checking again.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Sus(bot))
