# Cog Base
import discord
from discord.ext import commands
from discord import app_commands
import logging
from config.settings import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('base')

class Minecraft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    mc = app_commands.Group(name="mc", description="mc befehle")


    @mc.command(name="servercheck", description="checke ob der Server online ist")
    async def check_mcserver(self, interaction: discord.Interaction):
        asyncron = await test_function_1()
        await interaction.response.send_message(f"Test 0: {asyncron}")



async def setup(bot):
    await bot.add_cog(Minecraft(bot))