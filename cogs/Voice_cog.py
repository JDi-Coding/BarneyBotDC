import discord
from discord.ext import commands
import asyncio
from pytube import Playlist

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}  # Warteschlange für jeden Server
        self.current_song = {}  # Aktuell gespielter Song pro Server
        self.voice_clients = {}  # Voice Clients verwalten
        self.page_size = 5  # Anzahl von Songs pro Seite in der Playlist
        self.current_page = {}  # Aktuelle Seite für jede Guild

    # Hilfsfunktion zum Herunterladen eines Songs in einem separaten Thread
    async def download_audio(self, url: str):
        def run_yt_dlp():
            import yt_dlp as youtube_dl  # Import hier, um sicherzustellen, dass die Bibliothek verwendet wird
            ydl_opts = {
                'format': 'bestaudio',
                'noplaylist': 'True',  # Nur ein einzelnes Video herunterladen
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

    # Hilfsfunktion zum Spielen eines Songs
    async def play_music(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id not in self.queue or not self.queue[guild_id]:
            self.current_song[guild_id] = None
            return

        song_path, song_title, duration, uploader, webpage_url, thumbnail_url, requester = self.queue[guild_id].pop(0)
        self.current_song[guild_id] = (song_title, webpage_url)

        voice_client = self.voice_clients[guild_id]
        audio_source = discord.FFmpegPCMAudio(song_path)
        voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(self.check_queue(interaction), self.bot.loop))

        await interaction.followup.send(f"Jetzt wird abgespielt: [{song_title}]({webpage_url})", ephemeral=True)

    async def check_queue(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id in self.queue and self.queue[guild_id]:
            await self.play_music(interaction)
        else:
            self.current_song[guild_id] = None

    # /play [URL] - Spielt einen Song ab oder fügt ihn der Warteschlange hinzu
    @discord.app_commands.command(name="play", description="Spielt ein Lied von YouTube ab oder fügt es zur Warteschlange hinzu")
    async def play(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer(ephemeral=True)

        # Überprüfen, ob der Benutzer in einem Voice-Channel ist
        if not interaction.user.voice:
            await interaction.followup.send("Du musst in einem Voice-Channel sein, um diesen Befehl zu nutzen.", ephemeral=True)
            return

        # Bot tritt dem Voice-Channel bei, falls er noch nicht drin ist
        voice_channel = interaction.user.voice.channel
        guild_id = interaction.guild.id
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            voice_client = await voice_channel.connect()
            self.voice_clients[guild_id] = voice_client

        # Song zur Queue hinzufügen und abspielen
        try:
            if "playlist" in url:
                # Lade die Playlist herunter
                video_urls = self.get_video_urls(url)

                for video_url in video_urls:
                    # Download des Songs und zur Warteschlange hinzufügen
                    try:
                        song_path, song_title, duration, uploader, webpage_url, thumbnail_url = await self.download_audio(video_url)
                        requester = interaction.user.name
                        self.queue.setdefault(guild_id, []).append((song_path, song_title, duration, uploader, webpage_url, thumbnail_url, requester))
                    except Exception as e:
                        await interaction.followup.send(f"Fehler beim Hinzufügen des Songs: {e}", ephemeral=True)
                        return

                # Wenn gerade nichts gespielt wird, sofort abspielen
                if not voice_client.is_playing():
                    await self.play_music(interaction)
                else:
                    await interaction.followup.send(f"Die Playlist wurde zur Warteschlange hinzugefügt.", ephemeral=True)

            else:
                # Normalen Song abspielen
                song_path, song_title, duration, uploader, webpage_url, thumbnail_url = await self.download_audio(url)
                requester = interaction.user.name
                self.queue.setdefault(guild_id, []).append((song_path, song_title, duration, uploader, webpage_url, thumbnail_url, requester))

                # Wenn gerade nichts gespielt wird, sofort abspielen
                if not voice_client.is_playing():
                    await self.play_music(interaction)
                else:
                    await interaction.followup.send(f"{song_title} zur Warteschlange hinzugefügt.", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"Fehler beim Hinzufügen des Songs: {e}", ephemeral=True)

    # Funktion, um Video-URLs aus einer Playlist zu extrahieren
    def get_video_urls(self, playlist_url):
        playlist = Playlist(playlist_url)
        return [video_url for video_url in playlist.video_urls]

    # /stop - Stoppt die Musik und verlässt den Voice-Channel
    @discord.app_commands.command(name="stop", description="Stoppt die Musik und verlässt den Voice-Channel")
    async def stop(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_connected():
            self.queue[interaction.guild.id].clear()
            await voice_client.disconnect()
            await interaction.response.send_message("Musik gestoppt und Voice-Channel verlassen.", ephemeral=True)
        else:
            await interaction.response.send_message("Ich bin in keinem Voice-Channel.", ephemeral=True)

    # /pause - Pausiert die Musik
    @discord.app_commands.command(name="pause", description="Pausiert die Musik")
    async def pause(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("Musik pausiert.", ephemeral=True)
        else:
            await interaction.response.send_message("Momentan wird keine Musik abgespielt.", ephemeral=True)

    # /resume - Setzt die Musik fort
    @discord.app_commands.command(name="resume", description="Setzt die Musik fort")
    async def resume(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("Musik fortgesetzt.", ephemeral=True)
        else:
            await interaction.response.send_message("Es gibt nichts zum Fortsetzen.", ephemeral=True)

    # /playlist - Zeigt die aktuelle Warteschlange als Discord Embed an
    @discord.app_commands.command(name="playlist", description="Zeigt die aktuelle Playlist")
    async def show_playlist(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id not in self.current_page:
            self.current_page[guild_id] = 0  # Setzt die Startseite auf 0

        total_songs = len(self.queue[guild_id]) if guild_id in self.queue else 0
        if total_songs == 0:
            await interaction.response.send_message("Die Warteschlange ist leer.", ephemeral=True)
            return

        # Gesamtdauer berechnen
        total_duration = sum(song[2] for song in self.queue[guild_id])
        total_minutes, total_seconds = divmod(total_duration, 60)

        # Embed erstellen
        embed = discord.Embed(
            title=f"Playlist ({total_songs})",
            description="**Aktueller Song:**\n" + (f"**{self.current_song[guild_id][0]}**\n" if guild_id in self.current_song and self.current_song[guild_id] else "Kein Song wird gerade abgespielt."),
            color=discord.Color.blue()
        )
        
        # Thumbnail des aktuellen Songs hinzufügen
        if guild_id in self.current_song and self.current_song[guild_id]:
            thumbnail_url = self.queue[guild_id][0][5]  # Thumbnail des aktuellen Songs
            embed.set_thumbnail(url=thumbnail_url)

        # Warteschlange erstellen
        queue_list = ""
        start_index = self.current_page[guild_id] * self.page_size
        end_index = start_index + self.page_size
        for i in range(start_index, min(end_index, total_songs)):
            song_title = self.queue[guild_id][i][1]
            song_duration = self.queue[guild_id][i][2]
            requester = self.queue[guild_id][i][6]  # Der Benutzer, der das Lied angefordert hat
            minutes, seconds = divmod(song_duration, 60)
            queue_list += f"{i + 1}. {song_title} | {minutes}:{seconds:02} by {requester}\n"

        embed.add_field(name="Warteschlange", value=queue_list or "Keine Lieder in der Warteschlange.", inline=False)
        embed.add_field(name="Gesamtdauer", value=f"{total_minutes}:{total_seconds:02}", inline=False)

        # Buttons hinzufügen
        view = discord.ui.View(timeout=None)
        if self.current_page[guild_id] > 0:
            view.add_item(discord.ui.Button(label="Zurück", style=discord.ButtonStyle.secondary, custom_id="prev_page"))
        if end_index < total_songs:
            view.add_item(discord.ui.Button(label="Vor", style=discord.ButtonStyle.secondary, custom_id="next_page"))

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Zurück", style=discord.ButtonStyle.secondary)
    async def prev_page(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id in self.current_page and self.current_page[guild_id] > 0:
            self.current_page[guild_id] -= 1
            await self.show_playlist(interaction)

    @discord.ui.button(label="Vor", style=discord.ButtonStyle.secondary)
    async def next_page(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        total_songs = len(self.queue[guild_id]) if guild_id in self.queue else 0
        if guild_id in self.current_page and (self.current_page[guild_id] + 1) * self.page_size < total_songs:
            self.current_page[guild_id] += 1
            await self.show_playlist(interaction)

# Fügt den Cog dem Bot hinzu
async def setup(bot: commands.Bot):
    await bot.add_cog(Voice(bot))