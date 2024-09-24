# basic_cog.py
import discord
from discord.ext import commands
from discord import app_commands

class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def Ping(self, ctx):
        await ctx.send("Pong!")

    #GUILD_ID = discord.Object(id=911273680301084753)
    @discord.app_commands.command(name="hello", description="Sage Hallo zum Bot")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Hey {interaction.user.mention}!", ephemeral=True)

    @discord.app_commands.command(name="say", description="Lässe den Bot was Sagen.")
    async def say(self, interaction: discord.Interaction, say: str):
        await interaction.response.send_message(f"User {interaction.user.mention} told me to say {say}")

    @discord.app_commands.command(name="baum", description="Der Baum hat grüne Blätter und einen braunen Stamm.")
    async def baum(self, interaction: discord.Interaction):
        await interaction.response.send_message("Der Baum hat grüne Blätter und einen braunen Stamm.")

async def setup(bot):
    await bot.add_cog(BasicCog(bot))
