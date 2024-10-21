import logging
import re
import urllib.parse
import asyncio
from concurrent.futures import ThreadPoolExecutor

import discord
import yt_dlp
from pytube import Playlist as PytubePlaylist

from config.settings import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('player')

class Player:
    def __init__(self, bot):
        self.bot = bot
        self.youtube_base_url = 'https://www.youtube.com/'
        self.voice_client = None
        self.source = None
        self.default_volume = 0.25
        self.volume = 0.25
        self.default_bass = 0.0
        self.bass = 0.0
        self.default_treble = 0.0
        self.treble = 0.0
        self.ffmpeg_options = {
            'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': f'-vn -filter:a "volume={self.volume}, bass=g={self.bass}, treble=g={self.treble}"'
        }
        self.is_playing = False
        self.songs = []  # Warteschlange für Songs
        self.playlist = [] #Playlist zum Hin und Her Navigieren
        self.current_index = -1  # -1 bedeutet, dass kein Song aktuell gespielt wird
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.current_song = -1 # -1 = kein Current song
        self.current_song_url = None
        self.effects_chain = ""

    async def play(self, voice_client, link: str, added_by: str):
        if voice_client is None or not voice_client.is_connected():
            raise ValueError("Der Bot ist nicht mit einem Sprachkanal verbunden.")

        link = self.normalize_youtube_url(link)  # Normalisiere die URL

        if "youtube.com/playlist" in link:  #YouTube-Playlist
            try:
                yt_playlist = PytubePlaylist(link)  # Pytube-Playlist verwenden
                for url in yt_playlist:
                    cleanurl = self.normalize_youtube_url(url)
                    data = await self.bot.loop.run_in_executor(None, lambda: self.extract_video_info(cleanurl))
                    title, song_url, duration, thumbnail = data
                    converted_duration = self.convert_seconds_to_duration(duration)
                    self.add_song(title, song_url, cleanurl, converted_duration, thumbnail, added_by)
                    logger.info(f"Song hinzugefügt: {title}, Dauer: {duration}")
                if not self.is_playing:
                    await self.play_next(voice_client)
            except Exception as e:
                raise ValueError(f"An error occurred while fetching the playlist: {str(e)}")
        else: #Einzelnes YouTube-Video 
            try:
                data = await self.bot.loop.run_in_executor(None, lambda: self.extract_video_info(link))
                title, song_url, duration, thumbnail = data
                converted_duration = self.convert_seconds_to_duration(duration)
                self.add_song(title, song_url, link, converted_duration, thumbnail, added_by)
                logger.info(f"Song hinzugefügt: {title}, Dauer: {duration}")
                if not self.is_playing:
                    await self.play_next(voice_client)
            except Exception as e:
                raise ValueError(f"An error occurred while fetching the song: {str(e)}")
        # Überprüfen, ob ein Song erfolgreich hinzugefügt wurde
        if len(self.songs) > 0:
            return self.songs[-1]['title'], self.songs[-1].get('duration', '0'), self.songs[-1].get('thumbnail', '')
        else:
            return "Kein Titel", "0", ""
 
    def extract_video_info(self, link):
        """Hilfsfunktion, um die Video-Informationen abzurufen."""
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,  # Nur ein einzelnes Video verarbeiten, keine Playlists
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video = ydl.extract_info(link, download=False)
        # Extrahiere die Informationen
        title = video.get('title', 'Unknown Title') #Hole Title sonst Unknown title
        # Song URL: Hole die URL aus dem 'formats'-Schlüssel, falls 'url' nicht existiert
        song_url = video.get('url')  # Normalerweise hier
        if not song_url and 'formats' in video:
            song_url = video['formats'][0].get('url', '')
        if not song_url:
            raise ValueError(f"Could not retrieve song URL for the video '{title}'")
        duration = video.get('duration', 0)  # Dauer abrufen, standardmäßig 0
        thumbnail = video.get('thumbnail', '')  # Thumbnail abrufen
        return title, song_url, duration, thumbnail
       
    def normalize_youtube_url(self, url):
        """Normalizes various YouTube URL formats into a standard format and handles playlists."""
        parsed_url = urllib.parse.urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

        # Fall 1: Es ist ein Video-Link (normalisiere auf den Standard-Video-Link)
        if "youtube.com/watch" in base_url or "youtu.be" in base_url:
            if "v=" in parsed_url.query:
                video_id = urllib.parse.parse_qs(parsed_url.query)["v"][0]
                return f"https://www.youtube.com/watch?v={video_id}"
            elif len(parsed_url.path.split("/")) > 1:
                video_id = parsed_url.path.split("/")[-1]
                return f"https://www.youtube.com/watch?v={video_id}"

        # Fall 2: Es ist ein Playlist-Link (normalisiere und erkenne die Playlist-ID)
        elif "youtube.com/playlist" in base_url and "list=" in parsed_url.query:
            playlist_id = urllib.parse.parse_qs(parsed_url.query)["list"][0]
            return f"https://www.youtube.com/playlist?list={playlist_id}"

        return url
  
    def convert_seconds_to_duration(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes}:{seconds:02d}"

    def add_song(self, title: str, url: str, shorturl: str, duration: str, thumbnail: str, added_by: str)-> None:
        # Überprüfe, ob die Dauer im richtigen Format ist
        if not isinstance(duration, str) or not re.match(r'^\d+:\d{2}$|^\d+:\d{2}:\d{2}$', duration):
            logger.error(f"Ungültiges Dauerformat für den Song '{title}': {duration}")
            duration = "0:00"  # Setze auf einen Standardwert, wenn die Dauer ungültig ist   
        
        playlist_id = self.playlistcounter(self.songs)
        self.songs.append({
            'playlistid': playlist_id,
            'title': title,
            'url': url,
            'shorturl': shorturl,
            'duration': duration,
            'thumbnail': thumbnail,
            'added_by': added_by
        })
        self.playlist.append(
            [playlist_id, self.songs[-1]]
        )     
    
    def playlistcounter(self, playlist: list)->int:
        playlist_id = len(playlist)
        var = playlist_id + 1  # Addiere immer um 1 weil neuer Eintrag
        return var
       
    async def play_next(self, voice_client):
        """Play the next song in the queue if available."""
        if voice_client is None or not voice_client.is_connected():
            self.is_playing = False
            return  # Stoppe hier, wenn der Bot nicht verbunden ist
        if self.songs:
            next_song = self.songs.pop(0)  # Hole den nächsten Song
            current_song = next_song
            self.current_song_url = next_song['url']
            self.voice_client = voice_client
            self.source = discord.FFmpegPCMAudio(next_song['url'], **self.ffmpeg_options)
            voice_client.play(self.source, after=lambda e: self.bot.loop.create_task(self.play_next(voice_client)))
            self.set_current_song(current_song['playlistid'])  # Setze den aktuellen Song
            self.is_playing = True
            logger.info(f"Spiele den nächsten Song: {next_song['title']}")
            return next_song['title']
        else:
            self.is_playing = False
            
    def get_current_song(self):
        logger.info("get Current INDEX")
        if self.current_index >= 0:
            logger.info("CurrentIndex: " + str(self.current_index))
            current_playlist_index = self.playlist[self.current_index]
            return current_playlist_index[-1]
        return None

    def set_current_song(self, song: int):
        """Setze den aktuellen Song in der Warteschlange."""
        logger.info("set Current INDEX: " + str(song))
        self.current_index = song
        print(self.current_index)

    def pause(self, voice_client):
        if voice_client.is_playing():
            voice_client.pause()
            
    def resume(self, voice_client):
        if voice_client.is_paused():
            voice_client.resume()

    def stop(self, voice_client):
        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()

    async def change_volume(self, volume: float):
        if self.voice_client and self.voice_client.is_playing():
            # Stop the current audio and restart with the new volume
            logger.info(f"Changing Volume to {volume}")
            self.voice_client.stop()
            # Hier verwenden wir den Link, der bereits abgespielt wird, um die Lautstärke zu ändern
            self.source = discord.FFmpegPCMAudio(self.current_song_url, **self.update_effects(volume=volume))
            self.voice_client.play(self.source)
    
    async def change_bass(self, bass:float):
        if self.voice_client and self.voice_client.is_playing():
            # Stop the current audio and restart with the new bass
            logger.info(f"Changing bass to {bass}")
            self.voice_client.stop()
            #bass ändern
            self.source = discord.FFmpegPCMAudio(self.current_song_url, **self.update_effects(bass=bass))
            self.voice_client.play(self.source)

    async def reset_pl_effects(self):
        if self.voice_client and self.voice_client.is_playing():
            # Stop the current audio and restart with the new volume
            logger.info(f"Reseting Playlist Effects")
            self.voice_client.stop()
            # Hier verwenden wir den Link, der bereits abgespielt wird, um die Lautstärke zu ändern
            self.source = discord.FFmpegPCMAudio(self.current_song_url, **self.update_effects())
            self.voice_client.play(self.source)
   
    def update_effects(self, volume: float = None, bass: float = None, treble: float = None):
        # Update die Effektkette
        effects = []
        if volume is None and bass is None and treble is None:
            #Resete alles
            logger.info("Reset Audio Effects")
            self.volume = self.default_volume
            self.bass = self.default_bass
            self.treble = self.default_treble
            effects.append(f"volume={self.volume}")
            effects.append(f"bass=g={self.bass}")
            effects.append(f"treble=g={self.treble}")
        else:
            # Aktualisiere die Effecte
            if volume is not None:
                self.volume = volume
                logger.info(f"Setting Volume to {self.volume}")
            if bass is not None:
                self.bass = bass
                logger.info(f"Setting Bass to {self.bass}")
            if treble is not None:
                self.treble = treble
                logger.info(f"Setting Volume to {self.treble}")     
            #Hinzufügen wenn nicht Standart
            if self.volume != 0.25:
                effects.append(f"volume={self.volume}")
            if self.bass != 0.0:
                effects.append(f"bass=g={self.bass}")
            if self.treble != 0.0:
                effects.append(f"treble=g={self.treble}")
        # Verbinde alle Effekte in der Filterkette
        self.effects_chain = ", ".join(effects)
        logger.info(f"Updatet effect Chain: {self.effects_chain}")      
        mpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': f'-vn -filter:a "{self.effects_chain}"'
        }
        print(mpeg_options)
        return mpeg_options
            
        
#######################
#PLaylist
####################### 
    def is_empty(self):
        return len(self.songs) == 0

    def convert_duration_to_seconds(self, duration):
        if isinstance(duration, int):
            return duration
        if isinstance(duration, str):
            parts = duration.split(':')
            if len(parts) == 2:  # mm:ss Format
                minutes = int(parts[0])
                seconds = int(parts[1])
                return minutes * 60 + seconds
            elif len(parts) == 3:  # hh:mm:ss Format
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            else:
                raise ValueError("Invalid duration format")
        raise TypeError("Duration must be a string or int")

    def get_total_duration(self):
        """Berechnet die Gesamtdauer in Sekunden und gibt sie als 'Minuten: Sekunden'-String zurück"""
        total_seconds = sum(self.convert_duration_to_seconds(song['duration']) for song in self.songs)
        return self.seconds_to_min_sec(total_seconds)

    def seconds_to_min_sec(self, total_seconds):
        """Konvertiert Sekunden in das Format 'Minuten: Sekunden'"""
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02}"  # Stellt sicher, dass die Sekunden immer zweistellig sind

