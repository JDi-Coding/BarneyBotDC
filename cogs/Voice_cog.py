import discord
from discord.ext import commands
from discord import ui, ButtonStyle
import asyncio
import yt_dlp
import logging
from config.settings import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('voice')
class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Voice(bot))