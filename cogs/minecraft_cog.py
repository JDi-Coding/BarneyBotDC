# Cog Base
import traceback
#from curses.ascii import isdigit

import discord
from discord.ext import commands
from discord import app_commands
from cogs.games.minecraft.game import *
from mcstatus import JavaServer




class Minecraft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        from loggin import Logger
        self.log = Logger('minecraft').getLogger()

    mc = app_commands.Group(name="mc", description="mc befehle")

    @mc.command(name="servercheck", description="checke ob der Server online ist")
    async def check_mcserver(self, interaction: discord.Interaction, servername : str):
        await interaction.response.defer(ephemeral=True)
        await mcserver_lookup(interaction, servername)

async def setup(bot):
    await bot.add_cog(Minecraft(bot))