import discord
from discord.ext import commands
from discord import app_commands

class CogBase(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(CogBase(bot))

das ist ein Basis Cog einfach rauskopieren und eine eine ..._cog.py einfügen