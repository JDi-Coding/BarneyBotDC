import asyncio
import os

import discord
from discord import app_commands
from discord.ext import commands
from gtts import gTTS
from moviepy.editor import VideoFileClip


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.ffmpeg = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -filter:a "volume=0.25"'
        }
        from loggin import Logger
        self.log = Logger('voice').getLogger()

    VoiceGroup = app_commands.Group(name="voice", description="Voice commands")

    @VoiceGroup.command(name="joinvc", description="Join a specified voice channel.")
    async def join(self, interaction: discord.Interaction, channel_name: str):
        # Get the guild (server) the interaction was invoked in
        guild = interaction.guild
        
        # Find the voice channel by name
        channel = discord.utils.get(guild.voice_channels, name=channel_name)
        
        if channel is None:
            await interaction.response.send_message(f"Voice channel '{channel_name}' not found.", ephemeral=True)
            return

        # Connect to the voice channel
        await channel.connect()
        await interaction.response.send_message(f"Joined voice channel: {channel.name}", ephemeral=True)
        
    @VoiceGroup.command(name="join", description="Join the voice channel you are in.")
    async def joinvc(self, interaction: discord.Interaction):
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            await channel.connect()
            await interaction.response.send_message(f"Joined voice channel: {channel.name}", ephemeral=True)
        else:
            await interaction.response.send_message("You need to be in a voice channel to use this command.", ephemeral=True)

    @VoiceGroup.command(name="leave", description="Leave the voice channel.")
    async def leave(self, interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect(force=True)
            await interaction.response.send_message("Disconnected from the voice channel.", ephemeral=True)
        else:
            await interaction.response.send_message("I'm not in a voice channel.", ephemeral=True)

    @VoiceGroup.command(name="speak", description="Make the bot speak the given text.")
    async def speak(self, interaction: discord.Interaction, *, text: str):
        if interaction.guild.voice_client:
            tts = gTTS(text=text, lang='en')
            audio_file_path = "tts.mp3"
            tts.save(audio_file_path)

            interaction.guild.voice_client.play(discord.FFmpegPCMAudio(audio_file_path), after=lambda e: os.remove(audio_file_path))
            await interaction.response.send_message(f"Speaking: '{text}'", ephemeral=True)
        else:
            await interaction.response.send_message("I need to be in a voice channel to speak.", ephemeral=True)

    @VoiceGroup.command(name="join_and_speak", description="Join a specified voice channel and speak the given text.")
    async def join_and_speak(self, interaction: discord.Interaction, channel_name: str, *, text: str):
        # Find the voice channel by name
        guild = interaction.guild
        channel = discord.utils.get(guild.voice_channels, name=channel_name)

        if channel is None:
            await interaction.response.send_message(f"Voice channel '{channel_name}' not found.", ephemeral=True)
            return

        # Connect to the voice channel
        await channel.connect()
        
        # Generate the speech using gTTS
        tts = gTTS(text=text, lang='en')
        audio_file_path = "tts.mp3"
        tts.save(audio_file_path)

        # Play the audio file in the voice channel
        interaction.guild.voice_client.play(discord.FFmpegPCMAudio(audio_file_path), after=lambda e: os.remove(audio_file_path))
        
        await interaction.response.send_message(f"Joined voice channel: {channel.name} and speaking: '{text}'", ephemeral=True)
    @VoiceGroup.command(name="play_uploaded_audio", description="Upload an audio file for the bot to play.")
    async def play_uploaded_audio(self, interaction: discord.Interaction, audio_file: discord.Attachment):
        # Save the uploaded audio file
        file_path = f"./{audio_file.filename}"
        await audio_file.save(file_path)

        # Join the voice channel
        if interaction.user.voice is None:
            await interaction.response.send_message("You are not connected to a voice channel.")
            return

        voice_channel = interaction.user.voice.channel
        vc = await voice_channel.connect()
        await interaction.response.send_message("wird abgespielt", ephemeral=True)

        # Play the audio file
        vc.play(discord.FFmpegPCMAudio(file_path))

        # Wait for the audio to finish playing
        while vc.is_playing():
            pass
            await asyncio.sleep(1)

        # Disconnect from the voice channel and delete the file
        await vc.disconnect()
        os.remove(file_path)
        await interaction.response.send_message("Audio wird Abgespielt")

    @VoiceGroup.command(name="upload_video", description="Sende den Link für ein Video Achtung dauert laenger")
    async def upload_video(self, interaction: discord.Interaction, video_file: discord.Attachment):
        try:
            file_path = f"C:/Users/Anwender/Desktop/Projekte/Selfbot/StreamBot/videos/{video_file.filename}"
            await video_file.save(file_path)
            await interaction.response.defer(thinking=True, ephemeral=True)
            # Video laden und Informationen extrahieren
            clip = VideoFileClip(file_path)
            video_title = video_file.filename
            video_duration = clip.duration
            self.log.info(video_title)
            self.log.info(video_duration)
        except Exception as e:
            await interaction.followup.send(f"Hat nich geklapt {e}", ephemeral=True)
        finally:
            video_title = os.path.splitext(video_file.filename)[0]           
            await interaction.followup.send(f"Geklapt! Titel: {video_title}, Dauer: {video_duration} Sekunden", ephemeral=True)
            await interaction.followup.send(f"Fehler beim Ausführen des Befehls", ephemeral=True)
            await interaction.followup.send(f"$play {video_title}")


# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(Voice(bot))
