import logging
import re
import urllib.parse
import asyncio
from concurrent.futures import ThreadPoolExecutor

import discord
import yt_dlp
from pytube import Playlist as PytubePlaylist

class Player:
    def __init__(self, bot):
        self.bot = bot
        self.youtube_base_url = "https://www.youtube.com/"
        self.voice_client = None
        self.source = None
        self.default_volume = 0.30
        self.default_bass = 0.0
        self.default_treble = 0.0
        self.volume = self.default_volume
        self.bass = self.default_bass
        self.treble = self.default_treble

        self.ffmpeg_base_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        }

        self.is_playing = False
        self.tracks = []  # vereinheitlichte Struktur für Songs und Playlist
        self.current_index = -1
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.current_song_url = None
        self.effects_chain = ""
        self.looped = False

        from loggin import Logger
        self.log = Logger("player").getLogger()

    # ---------------------------------------------------------
    # Song hinzufügen / Playlist laden
    # ---------------------------------------------------------
    async def play(self, voice_client, link: str, added_by: str):
        if voice_client is None or not voice_client.is_connected():
            raise ValueError("Der Bot ist nicht mit einem Sprachkanal verbunden.")

        link = self.normalize_youtube_url(link)

        try:
            if "youtube.com/playlist" in link:
                await self._load_youtube_playlist(link, added_by)
            else:
                await self._load_single_song(link, added_by)

            if not self.is_playing:
                await self.play_next(voice_client)

            if self.tracks:
                last = self.tracks[-1]
                return last["title"], last["duration"], last["thumbnail"]
            return "Kein Titel", "0", ""

        except Exception as e:
            raise ValueError(f"Fehler beim Laden: {e}")

    async def _load_single_song(self, link, added_by):
        data = await self.bot.loop.run_in_executor(None, lambda: self.extract_video_info(link))
        title, song_url, duration, thumbnail = data
        converted_duration = self.convert_seconds_to_duration(duration)
        self.add_track(title, song_url, link, converted_duration, thumbnail, added_by, duration)
        self.log.info(f"Song hinzugefügt: {title}")

    async def _load_youtube_playlist(self, link, added_by):
        yt_playlist = PytubePlaylist(link)
        for url in yt_playlist:
            cleanurl = self.normalize_youtube_url(url)
            data = await self.bot.loop.run_in_executor(None, lambda: self.extract_video_info(cleanurl))
            title, song_url, duration, thumbnail = data
            converted_duration = self.convert_seconds_to_duration(duration)
            self.add_track(title, song_url, cleanurl, converted_duration, thumbnail, added_by, duration)
        self.log.info(f"Playlist hinzugefügt: {len(self.tracks)} Songs")

    # ---------------------------------------------------------
    # Song-Infos abrufen
    # ---------------------------------------------------------
    def extract_video_info(self, link):
        ydl_opts = {"format": "bestaudio/best", "noplaylist": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video = ydl.extract_info(link, download=False)

        title = video.get("title", "Unknown Title")
        song_url = video.get("url") or video["formats"][0].get("url", "")
        duration = video.get("duration", 0)
        thumbnail = video.get("thumbnail", "")
        return title, song_url, duration, thumbnail

    def normalize_youtube_url(self, url):
        parsed = urllib.parse.urlparse(url)
        if "youtu.be" in url:
            vid = parsed.path.strip("/")
            return f"https://www.youtube.com/watch?v={vid}"
        if "youtube.com/watch" in url and "v=" in parsed.query:
            vid = urllib.parse.parse_qs(parsed.query)["v"][0]
            return f"https://www.youtube.com/watch?v={vid}"
        if "youtube.com/playlist" in url and "list=" in parsed.query:
            pid = urllib.parse.parse_qs(parsed.query)["list"][0]
            return f"https://www.youtube.com/playlist?list={pid}"
        return url

    # ---------------------------------------------------------
    # Playlist-Handling
    # ---------------------------------------------------------
    def add_track(self, title, url, shorturl, duration, thumbnail, added_by, seconds):
        track_id = len(self.tracks) + 1
        self.tracks.append({
            "id": track_id,
            "title": title,
            "url": url,
            "shorturl": shorturl,
            "duration": duration if re.match(r"^\d+:\d{2}$|^\d+:\d{2}:\d{2}$", duration) else "0:00",
            "thumbnail": thumbnail,
            "added_by": added_by,
            "played": False,
            "seconds": seconds
        })

    def get_next_song(self):
        for track in self.tracks:
            if not track["played"] or self.looped is True:
                return track
        return None  # keine ungespielten Songs

    def mark_as_played(self, track):
        for t in self.tracks:
            if t["id"] == track["id"]:
                t["played"] = True
                break

    async def play_next(self, voice_client):
        if not voice_client or not voice_client.is_connected():
            self.is_playing = False
            return

        next_song = self.get_next_song()
        if not next_song:
            self.is_playing = False
            self.log.info("Keine weiteren Songs in der Playlist.")
            return

        self.mark_as_played(next_song)
        self.current_song_url = next_song["url"]
        self.voice_client = voice_client
        self.source = discord.FFmpegPCMAudio(next_song["url"], **self.update_effects())
        voice_client.play(self.source, after=lambda e: self.bot.loop.create_task(self.play_next(voice_client)))

        self.current_index = next_song["id"]
        self.is_playing = True
        self.log.info(f"Spiele jetzt: {next_song['title']}")

    def get_current_song(self):
        if self.current_index <= 0:
            return None
        for t in self.tracks:
            if t["id"] == self.current_index:
                return t
        return None

    # ---------------------------------------------------------
    # Audioeffekte / Steuerung
    # ---------------------------------------------------------
    def update_effects(self, volume=None, bass=None, treble=None):
        if volume is not None:
            self.volume = volume
        if bass is not None:
            self.bass = bass
        if treble is not None:
            self.treble = treble

        effects = [
            f"volume={self.volume}",
            f"bass=g={self.bass}",
            f"treble=g={self.treble}"
        ]
        filter_chain = ", ".join(effects)
        opts = self.ffmpeg_base_options | {"options": f'-vn -filter:a "{filter_chain}"'}
        self.log.debug(f"FFmpeg Filter: {filter_chain}")
        return opts

    def convert_seconds_to_duration(self, sec):
        m, s = divmod(sec, 60)
        return f"{m}:{s:02d}"

    # ---------------------------------------------------------
    # Steuerung
    # ---------------------------------------------------------
    def pause(self, vc):
        if vc.is_playing(): vc.pause()

    def resume(self, vc):
        if vc.is_paused(): vc.resume()

    def stop(self, vc):
        if vc.is_playing() or vc.is_paused():
            vc.stop()
            self.is_playing = False

    def is_empty(self):
        return not bool(self.tracks)
