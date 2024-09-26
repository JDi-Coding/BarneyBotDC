import discord

class PlaylistEmbed:
    def __init__(self, playlist):
        self.playlist = playlist
        self.current_page = 0
        self.max_songs_per_page = 5

    def create_embed(self):
        # Aktuell spielender Song und Thumbnail
        current_song = self.playlist.get_current_song()
        thumbnail_url = current_song['thumbnail'] if current_song else None
        embed = discord.Embed(
            title="🎵 Playlist [{}]".format(len(self.playlist.songs)),
            color=discord.Color.blue()
        )
        # Thumbnail hinzufügen
        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)
        else:
            embed.set_thumbnail(url="https://via.placeholder.com/150")  # Fallback Thumbnail
        # Aktueller Song
        if current_song:
            embed.add_field(
                name="Now Playing",
                value=f"[**{current_song['title']}**]({current_song['shorturl']})",
                inline=False
            )
        else:
            embed.add_field(name="Now Playing", value="No song is currently playing.", inline=False)
        # Songs auf der aktuellen Seite in einem einzigen Feld sammeln
        start_index = self.current_page * self.max_songs_per_page
        end_index = start_index + self.max_songs_per_page
        songs = self.playlist.songs[start_index:end_index]
        # Hier sammeln wir alle Songs in einem String
        song_list = ""
        for i, song in enumerate(songs, start=1):
            title = song['title']
            url = song['shorturl']
            duration = song['duration']
            added_by = song['added_by']
            # Füge den Song zur Liste hinzu
            song_list += f"Nr.{i}: [{title}]({url}) | Duration: {duration} | Added by: {added_by}\n"
        # Alle Songs in einem einzigen Feld hinzufügen
        if song_list:
            embed.add_field(
                name="Playlist",
                value=song_list,
                inline=False
            )
        else:
            embed.add_field(name="Songs", value="No songs in the playlist.", inline=False)
        # Gesamtdauer der Playlist
        total_duration = self.playlist.get_total_duration()
        embed.set_footer(text=f"Total Duration: {total_duration}")
        return embed

    def create_buttons(self):
        buttons = [
            discord.ui.Button(label="Back", custom_id="back"),
            discord.ui.Button(label="Next", custom_id="next"),
        ]
        return buttons

    def next_page(self):
        if (self.current_page + 1) * self.max_songs_per_page < len(self.playlist.songs):
            self.current_page += 1

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
