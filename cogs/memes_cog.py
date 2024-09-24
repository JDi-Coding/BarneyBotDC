# basic_cog.py
import discord
from discord.ext import commands
from discord import app_commands

class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="wow", description="Sendet ein wow GIF")
    async def wow(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Einfach nur wow:", file=discord.File('data\GIF\wow.gif'))

    @discord.app_commands.command(name="what", description="Sendet ein what GIF")
    async def wow(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="what", file=discord.File('data\GIF\what.gif'))

async def setup(bot):
    await bot.add_cog(Memes(bot))
