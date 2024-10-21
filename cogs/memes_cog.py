# basic_cog.py
import logging
import os
import random

import discord
from discord import app_commands
from discord.ext import commands



def get_meme_path(meme_dir: str):
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

class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        from loggin import Logger
        self.log = Logger('memes').getLogger()

    MemeGroup = app_commands.Group(name="meme", description="Alles rund um memes")

    @MemeGroup.command(name="wow", description="Sendet ein wow GIF")
    async def wow(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Einfach nur wow:", file=discord.File('data/GIF/wow.gif'))

    @MemeGroup.command(name="what", description="Sendet ein what GIF")
    async def what(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="what", file=discord.File('data/GIF/what.gif'))
 
    @MemeGroup.command(name="meme", description="Send a meme")
    async def meme(self, interaction: discord.Interaction):
        meme_path = get_meme_path('data/Memes')
        # Sende das Meme als Datei
        await interaction.response.send_message(file=discord.File(meme_path))
    
    @MemeGroup.command(name="germanmeme", description="Sendet ein zufaelliges Deutsches Meme")
    async def germanmeme(self, interaction: discord.Interaction):
        meme_path = get_meme_path('data/GerMemes')
        # Sende das Meme als Datei
        await interaction.response.send_message(file=discord.File(meme_path))

    @MemeGroup.command(name="offensivememe", description="sends a offensiv meme")
    async def offensivmeme(self, interaction: discord.Interaction):
        meme_path = get_meme_path('data/OffMemes')
        # Sende das Meme als Datei
        await interaction.response.send_message(file=discord.File(meme_path))

async def setup(bot):
    await bot.add_cog(Memes(bot))
