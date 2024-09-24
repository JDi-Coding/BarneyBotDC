# Cog Base
import discord
from discord.ext import commands
from discord import app_commands

class CogBase(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(CogBase(bot))

- das ist ein Basis Cog einfach rauskopieren und eine eine ..._cog.py einfügen

# Command Help
    help="",
    description="",
    brief="",
    enabled=True, #Enables the Command or Disable the Command [TRUE/FALSE]
    hidden=False #Hids the Command for !help altough !help ping shows still information [TRUE/FALSE]


- für Text Commands 

# Slash Command 

    @discord.app_commands.command(name="", description="", nsfw=False)
    async def (self, interaction: discord.Interaction):

- Für Slash Commands nach def den Funktionsnamen eingeben