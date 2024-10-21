import logging

import discord
from discord import app_commands
from discord.ext import commands

from config.config import PREMIUM_GUILD_IDS
from config.settings import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('bot')
import os
import yt_dlp
import asyncio

class DownloadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    DownloadGroup = app_commands.Group(name="download", description="download videos from the internet", guild_ids=PREMIUM_GUILD_IDS)

    #Command zum Downloaden von YT Videos wird in zukunft warscheinlich ausgelagert und erweitert
    @DownloadGroup.command(name="yt", description="downloads the specified youtube video")
    async def download(self, interaction: discord.Interaction, url: str):
        try:
            logger.info(f"URL: {url}")
            # Sende die Nachricht in den spezifischen Kanal
            # Video von der URL herunterladen
            await interaction.response.send_message("Video wird heruntergeladen, bitte warten...", ephemeral=True)
            # Definiere den Download-Pfad
            download_dir = "C:/Users/jason/Downloads/ytdownload"
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)

            # Option, um das Video herunterzuladen
            ydl_opts = {
                'outtmpl': f'{download_dir}/%(title)s.%(ext)s'#, #Speichert das Video mit Titel und Erweiterung
                #'format': 'best',  # Beste verfügbare Qualität
            }
            title = ""
            logger.info(f"pretitle: {title}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url)
                filename = ydl.prepare_filename(info)
                title = info.get('title', None)
                clean_title = title.replace(" ", "").replace("-", "")
            logger.info(f"Filename: , {filename}")
            logger.info(f"title:, {title}")
            logger.info(f"cleantitle: , {clean_title}")
            await interaction.followup.send(f"Das Video wurde erfolgreich heruntergeladen", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Fehler: {e}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(DownloadCog(bot))