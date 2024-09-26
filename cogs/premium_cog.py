import discord
from discord.ext import commands
from discord import app_commands
from config.config import PREMIUM_GUILD_IDS
from config.utils import has_premium_access
import logging
from config.settings import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('bot')

class Premium(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        
            
    Premium = app_commands.Group(name="premium", description="premium commands", guild_ids=PREMIUM_GUILD_IDS)
      
    @Premium.command(name="help", description="Premium-Funktion für Premium Server") 
    async def help(self, interaction: discord.Interaction):
        await interaction.response.send_message("Premium")
        
    @Premium.command(name="count", description="Zählt die Anzahl der Premium-Befehle und listet sie auf")
    async def count(self, interaction: discord.Interaction):
        # Zähle die Befehle in der Premium-Gruppe
        command_count = len(self.Premium.commands)        
        # Erstelle ein Embed-Objekt
        embed = discord.Embed(title="Premium Befehle", description=f"Es gibt {command_count} Premium-Befehle in der Gruppe.", color=discord.Color.blue())       
        # Füge jeden Befehl zur Embed-Nachricht hinzu
        for command in self.Premium.commands:
            embed.add_field(name=f"/{Premium.__name__} " + command.name, value=command.description, inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Premium(bot))