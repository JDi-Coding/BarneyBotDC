# basic_cog.py
import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import logging
from config.settings import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('memes')

class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def getMemePath(self, meme_dir: str):
        # Verzeichnis mit den Memes
        #meme_dir = 'data/Memes'
        # Liste alle Dateien im Verzeichnis auf
        all_files = os.listdir(meme_dir)
        # Filtere nur Bilder (du kannst Dateiendungen anpassen, falls nötig)
        meme_files = [file for file in all_files if file.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        # Wähle ein zufälliges Meme aus
        selected_meme = random.choice(meme_files)
        # Erstelle den vollständigen Pfad zur ausgewählten Datei
        meme_path = os.path.join(meme_dir, selected_meme)
        # Sende das Meme als Datei
        return meme_path





    @discord.app_commands.command(name="wow", description="Sendet ein wow GIF")
    async def wow(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Einfach nur wow:", file=discord.File('data/GIF/wow.gif'))

    @discord.app_commands.command(name="what", description="Sendet ein what GIF")
    async def what(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="what", file=discord.File('data/GIF/what.gif'))
 
    @discord.app_commands.command(name="meme", description="Send a meme")
    async def meme(self, interaction: discord.Interaction):
        meme_path = self.getMemePath('data/Memes')
        # Sende das Meme als Datei
        await interaction.response.send_message(file=discord.File(meme_path))
    
    @discord.app_commands.command(name="germanmeme", description="Sendet ein zufaelliges Deutsches Meme")
    async def germanmeme(self, interaction: discord.Interaction):
        meme_path = self.getMemePath('data/GerMemes')
        # Sende das Meme als Datei
        await interaction.response.send_message(file=discord.File(meme_path))

    @discord.app_commands.command(name="offensivememe", description="sends a offensiv meme")
    async def offensivmeme(self, interaction: discord.Interaction):
        meme_path = self.getMemePath('data/OffMemes')
        # Sende das Meme als Datei
        await interaction.response.send_message(file=discord.File(meme_path))




    #Befehl um alle Verfügbaren SlashBefehle anzuzeigen
    @commands.command(
            help="hope it was helpfull : )",
            description="this Command Shows every Slash-Command available in this Category. usage: [Prefix][Category]info",
            brief="-> Shows every Slash-Command",
            enabled=True, #Enables the Command or Disable the Command [TRUE/FALSE]
            hidden=False #Hids the Command for !help altough !help ping shows still information [TRUE/FALSE]
    )
    async def MemeInfo(self, ctx):
        # Alle /-Befehle des Bots
        commands_list = self.bot.tree.get_commands()
        # Filtere die Slash-Befehle, die zu dieser Klasse gehören
        meme_commands = [cmd.name for cmd in commands_list if isinstance(cmd, app_commands.Command) and cmd.binding == self]

        #Naricht mit allen Befehlen generieren
        if meme_commands:
            commands_str = "\n".join(f"/{cmd}" for cmd in meme_commands)
            await ctx.send(f"Verfügbare Meme-Slash-Befehle:\n{commands_str}")
        else:
            await ctx.send("Es gibt keine slash Befehle in dieser Kategorie")


async def setup(bot):
    await bot.add_cog(Memes(bot))
