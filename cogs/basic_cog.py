# basic_cog.py
import logging

import discord
from discord import app_commands
from discord import Interaction, InteractionResponse
from discord.ext import commands

#from config.settings import LOGGING_CONFIG
import  logging.config
#logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('basic')

class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    basic = app_commands.Group(name="basic", description="Alle Basis Commands ohne Nutzen")
    
    @basic.command(
        name="ping",
        description="Pinge den Bot an",
        nsfw=False
    )
    async def ping(self, interaction: discord.Interaction):
        logger.info("Pinged")
        await interaction.response.send_message(f"Ping!", ephemeral=True)

    @basic.command(name="hello", description="Sage Hallo zum Bot")
    async def hello(self, interaction: discord.Interaction):
            await interaction.response.send_message(f"Hey {interaction.user.mention}!", ephemeral=True)
    
    @basic.command(name="say", description="Lässe den Bot was Sagen.", nsfw=False)
    async def say(self, interaction: discord.Interaction, say: str):
        await interaction.response.send_message(f"User {interaction.user.mention} told me to say {say}")

    @basic.command(name="baum", description="Der Baum hat grüne Blätter und einen braunen Stamm.", nsfw=False)
    async def baum(self, interaction: discord.Interaction):
        await interaction.response.send_message("Der Baum hat grüne Blätter und einen braunen Stamm.")

    @basic.command(name="wer", description="Wer hat mich aufgerufen")
    async def wer(self, interaction: discord.Interaction):
        author = interaction.user
        await interaction.response.send_message(f"Der Befehl wurde von {author.name} aufgerufen.")

    #Befehl um alle Verfügbaren SlashBefehle anzuzeigen
    @commands.command(
            help="hope it was helpful : )",
            description="this Command Shows every Slash-Command available in this Category. usage: [Prefix][Category]info",
            brief="-> Shows every Slash-Command",
            enabled=True, #Enables the Command or Disable the Command [TRUE/FALSE]
            hidden=False #Hids the Command for !help although !help ping shows still information [TRUE/FALSE]
    )
    async def basicinfo(self, ctx):
        # Alle /-Befehle des Bots
        commands_list = self.bot.tree.get_commands()
        # Filtere die Slash-Befehle, die zu dieser Klasse gehören
        basic_commands = [cmd.name for cmd in commands_list if isinstance(cmd, app_commands.Command) and cmd.binding == self]

        #Naricht mit allen Befehlen generieren
        if basic_commands:
            commands_str = "\n".join(f"/{cmd}" for cmd in basic_commands)
            await ctx.send(f"Verfügbare Basic-Slash-Befehle:\n{commands_str}")
        else:
            await ctx.send("Es gibt keine slash Befehle in dieser Kategorie")
        




async def setup(bot):
    await bot.add_cog(BasicCog(bot))
