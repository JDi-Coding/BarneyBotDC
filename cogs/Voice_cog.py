# voice_cog.py
import discord
from discord.ext import commands
from discord import app_commands
import discord.opus
import yt_dlp as youtube_dl
import asyncio
import logging.config
logger = logging.getLogger('bot')
import os
import random
###################################################################################


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_song = None
        self.queue = []
###################################################################################

    # Hilfsfunktion zum Herunterladen und Abspielen von Audio
    async def download_audio(self, url: str):
        ydl_opts = {
            'format': 'bestaudio',
            'noplaylist': 'True',
            'quiet': 'True',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3')
            return filename, info['title']

###################################################################################

    # Funktion zum Abspielen von Musik
    async def play_music(self, interaction: discord.Interaction):
        if self.queue:
            voice_client = interaction.guild.voice_client
            song_path, song_title = self.queue.pop(0)  # Nimmt das erste Lied aus der Queue
            self.current_song = song_title
            audio_source = discord.FFmpegPCMAudio(song_path)
            voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(self.check_queue(interaction), self.bot.loop))
            await interaction.followup.send(f"Jetzt wird abgespielt: {song_title}", ephemeral=True)

###################################################################################
   
    # Überprüfen, ob die Queue weiter abgespielt werden soll
    async def check_queue(self, interaction: discord.Interaction):
        if self.queue:
            await self.play_music(interaction)
        else:
            self.current_song = None

###################################################################################

    # /play [URL] - Spielt ein Lied von YouTube (oder zukünftig anderen Plattformen)
    @discord.app_commands.command(name="play", description="Spielt ein Lied von YouTube ab")
    async def play(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer(ephemeral=True)  # Verhindert Timeout

        # Überprüfen, ob der Benutzer in einem Voice-Channel ist
        if not interaction.user.voice:
            await interaction.followup.send("Du musst in einem Voice-Channel sein, um diesen Befehl zu nutzen.", ephemeral=True)
            return

        # Bot tritt dem Voice-Channel bei, falls er noch nicht drin ist
        voice_channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            voice_client = await voice_channel.connect()

        # Läd das Audio herunter und fügt es zur Playlist hinzu
        song_path, song_title = await self.download_audio(url)
        self.queue.append((song_path, song_title))
        await interaction.followup.send(f"{song_title} wurde zur Playlist hinzugefügt.", ephemeral=True)

        # Wenn gerade nichts abgespielt wird, starte das Lied
        if not voice_client.is_playing():
            await self.play_music(interaction)

###################################################################################

    # /stop - Stoppt die Musik und verlässt den Voice-Channel
    @discord.app_commands.command(name="stop", description="Stoppt die Musik und verlässt den Voice-Channel")
    async def stop(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_connected():
            self.queue.clear()  # Leert die Playlist
            await voice_client.disconnect()
            await interaction.response.send_message("Musik gestoppt und Voice-Channel verlassen.", ephemeral=True)
        else:
            await interaction.response.send_message("Ich bin in keinem Voice-Channel.", ephemeral=True)

###################################################################################

    # /pause - Pausiert die Musik
    @discord.app_commands.command(name="pause", description="Pausiert die Musik")
    async def pause(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("Musik pausiert.", ephemeral=True)
        else:
            await interaction.response.send_message("Momentan wird keine Musik abgespielt.", ephemeral=True)

###################################################################################

    # /unpause - Setzt die Musik fort
    @discord.app_commands.command(name="unpause", description="Setzt die Musik fort")
    async def unpause(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("Musik fortgesetzt.", ephemeral=True)
        else:
            await interaction.response.send_message("Die Musik ist nicht pausiert.", ephemeral=True)

###################################################################################

    # /playlist - Zeigt die aktuelle Playlist an
    @discord.app_commands.command(name="playlist", description="Zeigt die aktuelle Playlist an")
    async def playlist(self, interaction: discord.Interaction):
        if self.queue:
            playlist_str = "\n".join([f"{i + 1}. {song[1]}" for i, song in enumerate(self.queue)])
            await interaction.response.send_message(f"Aktuelle Playlist:\n{playlist_str}", ephemeral=True)
        else:
            await interaction.response.send_message("Die Playlist ist leer.", ephemeral=True)

###################################################################################

    # Slash-Befehl: Bot tritt dem Voice-Channel bei, in dem sich der Nutzer befindet
    @discord.app_commands.command(name="join", description="Bot tritt dem Voice-Channel bei, in dem du dich befindest.")
    async def join(self, interaction: discord.Interaction):
        # Überprüfen, ob der Nutzer in einem Voice-Channel ist
        if interaction.user.voice:
            voice_channel = interaction.user.voice.channel
            # Überprüfen, ob der Bot bereits in einem Voice-Channel ist
            if interaction.guild.voice_client is not None:
                await interaction.guild.voice_client.move_to(voice_channel)
                await interaction.response.send_message(f"Bin bereits in einem anderen Channel, bewege mich jetzt zu {voice_channel.name}.", ephemeral=True)
            else:
                # Bot tritt dem Voice-Channel bei
                await voice_channel.connect()
                await interaction.response.send_message(f"Ich bin jetzt dem Voice-Channel {voice_channel.name} beigetreten.", ephemeral=True)
                logger.info("Joined Voice Channel")
        else:
            # Nutzer ist nicht in einem Voice-Channel
            await interaction.response.send_message("Du bist in keinem Voice-Channel.", ephemeral=True)

###################################################################################

    # Slash-Befehl: Bot verlässt den Voice-Channel
    @discord.app_commands.command(name="leave", description="Bot verlässt den Voice-Channel.")
    async def leave(self, interaction: discord.Interaction):
        # Überprüfen, ob der Bot in einem Voice-Channel ist
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("Ich habe den Voice-Channel verlassen.", ephemeral=True)
            logger.info("Left Voice Channel")
        else:
            # Bot ist in keinem Voice-Channel
            await interaction.response.send_message("Ich bin in keinem Voice-Channel.", ephemeral=True)

###################################################################################

    # Befehl zum Abspielen einer zufälligen Audiodatei
    @discord.app_commands.command(name="makesound", description="Spielt eine zufällige Audiodatei ab")
    async def makesound(self, interaction: discord.Interaction):
        # Überprüfe, ob der Bot bereits in einem Voice-Channel ist
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            await interaction.response.send_message("Ich bin nicht in einem Voice-Channel. Nutze zuerst /join.", ephemeral=True)
            return
        # Verzeichnis mit den Audiodateien
        sound_dir = 'data/sounds'   
        # Liste alle Audiodateien im Verzeichnis auf
        all_files = os.listdir(sound_dir)
        sound_files = [file for file in all_files if file.endswith(('.mp3', '.wav'))]
        # Überprüfe, ob Audiodateien vorhanden sind
        if not sound_files:
            await interaction.response.send_message("Es gibt keine Audiodateien im Verzeichnis.", ephemeral=True)
            return
        # Wähle eine zufällige Audiodatei aus
        selected_sound = random.choice(sound_files)
        sound_path = os.path.join(sound_dir, selected_sound)
        # Spielt die Audiodatei ab
        audio_source = discord.FFmpegPCMAudio(sound_path)
        if not voice_client.is_playing():
            voice_client.play(audio_source)
            await interaction.response.send_message(f"Spiele Sound: {selected_sound}", ephemeral=True)
            logger.info(f"Playing sound: {selected_sound}")
        else:
            await interaction.response.send_message("Es wird bereits ein Sound abgespielt.", ephemeral=True)

###################################################################################

    #Befehl um alle Verfügbaren SlashBefehle anzuzeigen
    @commands.command(
            help="hope it was helpfull : )",
            description="this Command Shows every Slash-Command available in this Category. usage: [Prefix][Category]info",
            brief="-> Shows every Slash-Command",
            enabled=True, #Enables the Command or Disable the Command [TRUE/FALSE]
            hidden=False #Hids the Command for !help altough !help ping shows still information [TRUE/FALSE]
    )
    async def VCInfo(self, ctx):
        # Alle /-Befehle des Bots
        commands_list = self.bot.tree.get_commands()
        # Filtere die Slash-Befehle, die zu dieser Klasse gehören
        meme_commands = [cmd.name for cmd in commands_list if isinstance(cmd, app_commands.Command) and cmd.binding == self]
        #Naricht mit allen Befehlen generieren
        if meme_commands:
            commands_str = "\n".join(f"/{cmd}" for cmd in meme_commands)
            await ctx.send(f"Verfügbare VC-Slash-Befehle:\n{commands_str}")
        else:
            await ctx.send("Es gibt keine slash Befehle in dieser Kategorie")

###################################################################################

async def setup(bot):
    await bot.add_cog(Voice(bot))
