
import discord
from discord import app_commands
from discord.ext import commands

from config.config import PREMIUM_GUILD_IDS
from config import settings



from cogs.download.download import Download

import logging
#logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger('bot')


class DownloadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    DownloadGroup = app_commands.Group(name="download", description="download videos from the internet", guild_ids=PREMIUM_GUILD_IDS)

    #Command zum Downloaden von YT Videos
    @DownloadGroup.command(name="yt", description="downloads the specified youtube video")
    async def download(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer(thinking=True, ephemeral=True)
        try:
            Download(url)
            await interaction.edit_original_response(content="Video Heruntergeladen")
        except Exception as e:
            logger.error(f"Error: async def download: {e}")
            await  interaction.edit_original_response(content=f"Fehler beim Herunterladen: {e}")


async def setup(bot):
    await bot.add_cog(DownloadCog(bot))