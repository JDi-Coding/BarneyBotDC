import discord
from discord.ext import commands
from discord import ui, ButtonStyle
import asyncio
import yt_dlp

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Voice(bot))