# Cog Base
import traceback
#from curses.ascii import isdigit

import discord
from discord.ext import commands
from discord import app_commands
import logging
#from config.settings import LOGGING_CONFIG
#logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('minecraft')
from cogs.games.minecraft.game import *
from mcstatus import JavaServer




class Minecraft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    mc = app_commands.Group(name="mc", description="mc befehle")

    @mc.command(name="servercheck", description="checke ob der Server online ist")
    async def check_mcserver(self, interaction: discord.Interaction, servername : str):
        await interaction.response.defer(ephemeral=True)
        await mcserver_lookup(interaction, servername)

async def setup(bot):
    await bot.add_cog(Minecraft(bot))