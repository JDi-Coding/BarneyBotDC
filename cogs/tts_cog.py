import discord
from discord.ext import commands
from discord import app_commands
import logging
from config.settings import LOGGING_CONFIG
from gtts import gTTS
import os

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('base')


class TTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    TTSGroup = app_commands.Group(name="tts", description="tts")

    @TTSGroup.command(name="speak", description="Converts text to speech and plays it in a voice channel", nsfw=False)
    async def speak(self, interaction: discord.Interaction, text: str):
        try:
            # Check if the user is in a voice channel
            if interaction.user.voice:
                # Connect to the user's voice channel if not already connected
                voice_channel = interaction.user.voice.channel
                voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
                if not voice_client:
                    voice_client = await voice_channel.connect()
                # Convert the text to speech using gTTS
                tts = gTTS(text=text, lang='en')
                tts.save("tts.mp3")
                # Play the audio file using FFmpeg
                if not voice_client.is_playing():
                    voice_client.play(
                        discord.FFmpegPCMAudio("tts.mp3"),
                        after=lambda e: os.remove("tts.mp3") if os.path.exists("tts.mp3") else None
                    )
                    await interaction.response.send_message(f"Playing TTS in {voice_channel.mention}", ephemeral=True)
                else:
                    await interaction.response.send_message("I'm already playing audio.", ephemeral=True)
            else:
                # If the user is not in a voice channel
                await interaction.response.send_message("You need to be in a voice channel for me to join!", ephemeral=True)
        except Exception as tts_exception:
            logger.error(f"Error in speak: {tts_exception}")

async def setup(bot):
    await bot.add_cog(TTS(bot))