# basic_cog.py
import discord
from discord.ext import commands
from discord import app_commands
import logging
from config.settings import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('bot')

class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
            help="hope it was helpfull : )",
            description="Simple Ping Pong type [Prefix]Ping Bot Writes Pong and Tags you",
            brief="-> Ping Pong Command",
            enabled=True, #Enables the Command or Disable the Command [TRUE/FALSE]
            hidden=False #Hids the Command for !help altough !help ping shows still information [TRUE/FALSE]
    )
    async def Ping(self, ctx):
        await ctx.send("Pong!")

    #GUILD_ID = discord.Object(id=911273680301084753)
    @discord.app_commands.command(name="hello", description="Sage Hallo zum Bot", nsfw=False)
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Hey {interaction.user.mention}!", ephemeral=True)

    @discord.app_commands.command(name="say", description="Lässe den Bot was Sagen.", nsfw=False)
    async def say(self, interaction: discord.Interaction, say: str):
        await interaction.response.send_message(f"User {interaction.user.mention} told me to say {say}")

    @discord.app_commands.command(name="baum", description="Der Baum hat grüne Blätter und einen braunen Stamm.", nsfw=False)
    async def baum(self, interaction: discord.Interaction):
        await interaction.response.send_message("Der Baum hat grüne Blätter und einen braunen Stamm.")

    @discord.app_commands.command(name="wer", description="Wer hat mich aufgerufen")
    async def wer(self, interaction: discord.Interaction):
        author = interaction.user
        await interaction.response.send_message(f"Der Befehl wurde von {author.name} aufgerufen.")

    #Befehl um alle Verfügbaren SlashBefehle anzuzeigen
    @commands.command(
            help="hope it was helpfull : )",
            description="this Command Shows every Slash-Command available in this Category. usage: [Prefix][Category]info",
            brief="-> Shows every Slash-Command",
            enabled=True, #Enables the Command or Disable the Command [TRUE/FALSE]
            hidden=False #Hids the Command for !help altough !help ping shows still information [TRUE/FALSE]
    )
    async def BasicInfo(self, ctx):
        # Alle /-Befehle des Bots
        commands_list = self.bot.tree.get_commands()
        # Filtere die Slash-Befehle, die zu dieser Klasse gehören
        meme_commands = [cmd.name for cmd in commands_list if isinstance(cmd, app_commands.Command) and cmd.binding == self]

        #Naricht mit allen Befehlen generieren
        if meme_commands:
            commands_str = "\n".join(f"/{cmd}" for cmd in meme_commands)
            await ctx.send(f"Verfügbare Basic-Slash-Befehle:\n{commands_str}")
        else:
            await ctx.send("Es gibt keine slash Befehle in dieser Kategorie")




async def setup(bot):
    await bot.add_cog(BasicCog(bot))
