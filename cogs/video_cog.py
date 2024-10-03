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

class VideoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    VideoGroup = app_commands.Group(name="video", description="base", guild_ids=PREMIUM_GUILD_IDS)
    @VideoGroup.command(name="playvidbyurl", description="Sendet einen YouTube-Link in einen speziellen Kanal und lädt das Video herunter")
    async def play_vid_by_url(self, interaction: discord.Interaction, url: str):
        try:
            # Spezifische Guild-ID (Server-ID) und Channel-ID (Kanal-ID)
            guild_id = 911273680301084753  # Ersetze durch die Guild-ID des Servers
            channel_id = 911273710546202644  # Ersetze durch die Channel-ID des Kana
            print(url)
            # Hole die Guild (Server) und den Channel (Kanal)
            guild = self.bot.get_guild(guild_id)
            if guild is not None:
                channel = guild.get_channel(channel_id)
                if channel is not None:
                    # Sende die Nachricht in den spezifischen Kanal
                    # Video von der URL herunterladen
                    await interaction.response.send_message("Video wird heruntergeladen, bitte warten...", ephemeral=True)
                    # Definiere den Download-Pfad
                    download_dir = "E:/Projekte/discordprojects/SelfBot/StreamBot/videos"
                    if not os.path.exists(download_dir):
                        os.makedirs(download_dir)
                    
                    # Option, um das Video herunterzuladen
                    ydl_opts = {
                        'outtmpl': f'{download_dir}/%(title)s.%(ext)s',  # Speichert das Video mit Titel und Erweiterung
                        'format': 'best',  # Beste verfügbare Qualität
                    }
                    title = ""
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url)
                        filename = ydl.prepare_filename(info)
                        title = info.get('title', None)
                        clean_title = title.replace(" ", "").replace("-", "")
                        
                    print("Filename: ", filename)
                    print("title:", title)
                    print("cleantitle: ", clean_title)
                    # Entferne Leerzeichen aus dem Dateinamen
                    new_filename = filename.replace(" ", "")
                    print("newFilename: ", new_filename)
                    os.rename(filename, new_filename)

                    await interaction.followup.send(f"Das Video wurde erfolgreich heruntergeladen und im Kanal {channel.name} abgespielt.", ephemeral=True)
                    await channel.send(f"$refresh")
                    await asyncio.sleep(1)
                    await channel.send(f"$play {clean_title}")
                else:
                    await interaction.response.send_message(f"Kanal mit der ID {channel_id} nicht gefunden.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Server mit der ID {guild_id} nicht gefunden.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Fehler beim Senden der Nachricht: {e}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(VideoCog(bot))