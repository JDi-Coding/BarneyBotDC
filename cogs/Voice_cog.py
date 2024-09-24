import discord
from discord.ext import commands
import asyncio
from pytube import Playlist

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}
        self.current_song = {}
        self.voice_clients = {}
        self.page_size = 5
        self.current_page = {}
        self.looping = {}  # Um Looping-Status zu speichern
        self.volume = {}  # Um Lautstärke pro Server zu speichern

    async def download_audio(self, url: str):
        def run_yt_dlp():
            import yt_dlp as youtube_dl
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
                }],
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info).replace('.webm', '.mp3')
                return filename, info['title'], info.get('duration', 0), info['uploader'], info['webpage_url'], info.get('thumbnail')

        return await asyncio.to_thread(run_yt_dlp)

    async def play_music(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id not in self.queue or not self.queue[guild_id]:
            self.current_song[guild_id] = None
            return

        song_path, song_title, duration, uploader, webpage_url, thumbnail_url, requester = self.queue[guild_id].pop(0)
        self.current_song[guild_id] = (song_title, webpage_url)

        voice_client = self.voice_clients[guild_id]
        audio_source = discord.FFmpegPCMAudio(song_path, options=f'-filter:a "volume={self.volume.get(guild_id, 1.0)}"')

        voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(self.check_queue(interaction), self.bot.loop))

        await interaction.followup.send(f"Jetzt wird abgespielt: [{song_title}]({webpage_url})", ephemeral=True)

    async def check_queue(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id in self.queue and self.queue[guild_id]:
            await self.play_music(interaction)
        else:
            self.current_song[guild_id] = None

    @discord.app_commands.command(name="play", description="Spielt ein Lied von YouTube ab oder fügt es zur Warteschlange hinzu")
    async def play(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer(ephemeral=True)
        if not interaction.user.voice:
            await interaction.followup.send("Du musst in einem Voice-Channel sein, um diesen Befehl zu nutzen.", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel
        guild_id = interaction.guild.id
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            voice_client = await voice_channel.connect()
            self.voice_clients[guild_id] = voice_client

        try:
            if "playlist" in url:
                video_urls = self.get_video_urls(url)

                for video_url in video_urls:
                    try:
                        song_path, song_title, duration, uploader, webpage_url, thumbnail_url = await self.download_audio(video_url)
                        requester = interaction.user.name
                        self.queue.setdefault(guild_id, []).append((song_path, song_title, duration, uploader, webpage_url, thumbnail_url, requester))

                        if not voice_client.is_playing() and len(self.queue[guild_id]) == 1:
                            await self.play_music(interaction)
                    except Exception as e:
                        await interaction.followup.send(f"Fehler beim Hinzufügen des Songs: {e}", ephemeral=True)
                        return

                await interaction.followup.send(f"Die Playlist wurde zur Warteschlange hinzugefügt.", ephemeral=True)

            else:
                song_path, song_title, duration, uploader, webpage_url, thumbnail_url = await self.download_audio(url)
                requester = interaction.user.name
                self.queue.setdefault(guild_id, []).append((song_path, song_title, duration, uploader, webpage_url, thumbnail_url, requester))

                if not voice_client.is_playing():
                    await self.play_music(interaction)
                else:
                    await interaction.followup.send(f"{song_title} zur Warteschlange hinzugefügt.", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"Fehler beim Hinzufügen des Songs: {e}", ephemeral=True)

    def get_video_urls(self, playlist_url):
        playlist = Playlist(playlist_url)
        return [video_url for video_url in playlist.video_urls]

    @discord.app_commands.command(name="stop", description="Stoppt die Musik und verlässt den Voice-Channel")
    async def stop(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_connected():
            self.queue[interaction.guild.id].clear()
            await voice_client.disconnect()
            await interaction.response.send_message("Musik gestoppt und Voice-Channel verlassen.", ephemeral=True)
        else:
            await interaction.response.send_message("Ich bin in keinem Voice-Channel.", ephemeral=True)
    # FIXME: Skipt aber Command 'skip' raised an exception: NotFound: 404 Not Found (error code: 10015): Unknown Webhook
    @discord.app_commands.command(name="skip", description="Überspringt den aktuellen Song")
    async def skip(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()  # Stoppt den aktuellen Song
            await self.play_music(interaction)  # Spielt den nächsten Song
            await interaction.response.send_message("Aktueller Song übersprungen.", ephemeral=True)
        else:
            await interaction.response.send_message("Momentan wird keine Musik abgespielt.", ephemeral=True)

    @discord.app_commands.command(name="loop", description="Schaltet das Looping für den aktuellen Song oder die gesamte Playlist um")
    async def loop(self, interaction: discord.Interaction, mode: str = 'song'):
        guild_id = interaction.guild.id
        if mode not in ['song', 'playlist']:
            await interaction.response.send_message("Bitte wähle 'song' oder 'playlist' als Modus.", ephemeral=True)
            return

        self.looping[guild_id] = mode
        if mode == 'song':
            await interaction.response.send_message("Aktueller Song wird in einer Schleife abgespielt.", ephemeral=True)
        else:
            await interaction.response.send_message("Die gesamte Playlist wird in einer Schleife abgespielt.", ephemeral=True)

    async def play_with_loop(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id in self.queue and self.queue[guild_id]:
            if guild_id in self.looping:
                mode = self.looping[guild_id]
                if mode == 'song':
                    self.queue[guild_id].insert(0, self.queue[guild_id][0])  # Aktuellen Song wieder an die Warteschlange anfügen
                elif mode == 'playlist':
                    # Playlist wird wiederholt
                    song_path, song_title, duration, uploader, webpage_url, thumbnail_url, requester = self.queue[guild_id][0]
                    self.queue[guild_id].append((song_path, song_title, duration, uploader, webpage_url, thumbnail_url, requester))  # Playlist erneut anfügen

            await self.play_music(interaction)  # Nächsten Song spielen
    # FIXME: Command 'bassboost' raised an exception: AttributeError: 'FFmpegPCMAudio' object has no attribute 'url'
    @discord.app_commands.command(name="bassboost", description="Erhöht die Bassfrequenzen des aktuell abgespielten Songs")
    async def bassboost(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            # Erhöhen der Bassfrequenzen (Betriebsfilter anpassen)
            audio_source = discord.FFmpegPCMAudio(voice_client.source.url, options='-filter:a "equalizer=f=60:width_type=h:w=10000:g=10"')
            voice_client.stop()
            voice_client.play(audio_source)
            await interaction.response.send_message("Bassboost aktiviert!", ephemeral=True)
        else:
            await interaction.response.send_message("Momentan wird keine Musik abgespielt.", ephemeral=True)
    # FIXME: Ändert nix
    @discord.app_commands.command(name="volume", description="Setzt die Lautstärke")
    async def volume(self, interaction: discord.Interaction, volume: int):
        guild_id = interaction.guild.id
        if 0 <= volume <= 100:
            self.volume[guild_id] = volume / 100.0  # Lautstärke zwischen 0 und 1
            await interaction.response.send_message(f"Lautstärke auf {volume}% gesetzt.", ephemeral=True)
        else:
            await interaction.response.send_message("Bitte wähle einen Wert zwischen 0 und 100.", ephemeral=True)


    @discord.app_commands.command(name="playlist", description="Zeigt die aktuelle Playlist")
    async def show_playlist(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id not in self.queue or not self.queue[guild_id]:
            await interaction.response.send_message("Die Warteschlange ist leer.", ephemeral=True)
            return

        # Playlist anzeigen
        embed = discord.Embed(title="Aktuelle Warteschlange", color=discord.Color.blue())
        total_duration = sum(song[2] for song in self.queue[guild_id])
        total_minutes, total_seconds = divmod(total_duration, 60)

        queue_list = ""
        for i, song in enumerate(self.queue[guild_id]):
            song_title = song[1]
            song_duration = song[2]
            requester = song[6]  # Der Benutzer, der das Lied angefordert hat
            minutes, seconds = divmod(song_duration, 60)
            queue_list += f"{i + 1}. {song_title} | {minutes}:{seconds:02} by {requester}\n"

        embed.add_field(name="Warteschlange", value=queue_list or "Keine Lieder in der Warteschlange.", inline=False)
        embed.add_field(name="Gesamtdauer", value=f"{total_minutes}:{total_seconds:02}", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

# Fügt den Cog dem Bot hinzu
async def setup(bot: commands.Bot):
    await bot.add_cog(Voice(bot))
