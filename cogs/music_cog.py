import discord
from discord.ext import commands
from discord import app_commands
from cogs.Music.player import Player
from cogs.Music.playlist_embed import PlaylistEmbed
import logging
from config.settings import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('music')

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.player = Player(bot)  # Player-Instanz bleibt

    def convert_to_float(self, value: str) -> float:
        """Hilfsfunktion, um Komma in Punkt zu ändern und String in Float umzuwandeln."""
        value = value.replace(',', '.')  # Ersetze Komma mit Punkt
        try:
            return float(value)  # Konvertiere zu Float
        except ValueError:
            raise ValueError(f"Cannot convert '{value}' to float")
    
    MusicGroup = app_commands.Group(name="music", description="lass den bot music spielen")
           
    @MusicGroup.command(name="play", description="Play a song from a YouTube link.")
    async def play(self, interaction: discord.Interaction, link: str):
        # Check if the user is in a voice channel
        if interaction.user.voice is None:
            await interaction.response.send_message("You need to be in a voice channel to play music.", ephemeral=True)
            return
        # Acknowledge the interaction immediately
        await interaction.response.defer(thinking=True, ephemeral=True)
        voice_client = discord.utils.get(self.voice_clients.values(), guild=interaction.guild)
        # Check if the bot is already connected to a voice channel
        if voice_client is None:
            # Connect to the voice channel
            voice_client = await interaction.user.voice.channel.connect()
            self.voice_clients[interaction.guild.id] = voice_client
        # Play the song using the Player class
        try:
            added_by = interaction.user.name
            #print("added_by: ", added_by) 
            title, duration, thumbnail = await self.player.play(voice_client, link, added_by)  # Get duration and thumbnail
            await interaction.followup.send(f"Now playing: [**{title}**]({link})", ephemeral=True)
        except ValueError as e:
            await interaction.followup.send(str(e), ephemeral=True)

    @MusicGroup.command(name="pause", description="Pause the current song.")
    async def pause(self, interaction: discord.Interaction):
        voice_client = discord.utils.get(self.voice_clients.values(), guild=interaction.guild)
        if voice_client:
            self.player.pause(voice_client)
            await interaction.response.send_message("Paused the current song.", ephemeral=True)
        else:
            await interaction.response.send_message("No song is currently playing.", ephemeral=True)

    @MusicGroup.command(name="resume", description="Resume the current song.")
    async def resume(self, interaction: discord.Interaction):
        voice_client = discord.utils.get(self.voice_clients.values(), guild=interaction.guild)
        if voice_client:
            self.player.resume(voice_client)
            await interaction.response.send_message("Resumed the current song.", ephemeral=True)
        else:
            await interaction.response.send_message("The current song is not paused.", ephemeral=True)

    @MusicGroup.command(name="stop", description="Stop the music and leave the voice channel.")
    async def stop(self, interaction: discord.Interaction):
        voice_client = discord.utils.get(self.voice_clients.values(), guild=interaction.guild)
        if voice_client:
            self.player.stop(voice_client)
            await voice_client.disconnect()
            del self.voice_clients[interaction.guild.id]
            await interaction.response.send_message("Stopped playing and left the voice channel.", ephemeral=True)
        else:
            await interaction.response.send_message("I'm not connected to a voice channel.", ephemeral=True)

    @MusicGroup.command(name="skip", description="skip songs")
    async def skip(self, interaction: discord.interactions):
        print()
        await interaction.response.send_message("Skiped", ephemeral=True)
    
    @MusicGroup.command(name="shuffle", description="shuffelt die Playlist")
    async def shuffle(self, interaction: discord.interactions):
        print()
        await interaction.response.send_message("Shuffle", ephemeral=True)

    @MusicGroup.command(name="loop", description="loopt die Ganze PLaylist oder einzelne Songs")
    async def loop(self, interaction: discord.interactions):
        print()
        await interaction.response.send_message("looped", ephemeral=True)

    @MusicGroup.command(name="remove", description="removed titel aus der Playlist")
    async def remove(self, interaction: discord.interactions):
        print()
        await interaction.response.send_message("removed", ephemeral=True) 
   
    @MusicGroup.command(name="volume", description="Setzt die Lautstärke")
    async def volume(self, interaction: discord.Interaction, volume: str):
        try:
            volume_float = self.convert_to_float(volume)            
            # Überprüfe, ob der Wert im gültigen Bereich liegt
            if 0.0 <= volume_float <= 3.0:
                await self.player.change_volume(volume_float)  # Lautstärke ändern
                await interaction.response.send_message(f"Volume changed to {volume_float}", ephemeral=True)
            else:
                await interaction.response.send_message("Volume must be between 0 and 3.", ephemeral=True)
        except ValueError as e:
            logger.error(str(e))
            await interaction.response.send_message("Wert muss Zwischen 0.01 und 3.0 sein", ephemeral=True)
  
    @MusicGroup.command(name="bass", description="Boosted den bass nutze bitte , statt .")
    async def bass(self, interaction: discord.interactions, bass: float):
        try:
            bass_float = self.convert_to_float(bass)            
            # Überprüfe, ob der Wert im gültigen Bereich liegt
            if 0.0 <= bass_float <= 3.0:
                await self.player.change_volume(bass_float)  # Lautstärke ändern
                await interaction.response.send_message(f"Bss changed to {bass_float}", ephemeral=True)
            else:
                await interaction.response.send_message("Bass must be between 0 and 3.", ephemeral=True)
        except ValueError as e:
            logger.error(str(e))
            await interaction.response.send_message("Wert muss Zwischen 0.01 und 3.0 sein", ephemeral=True)
    @MusicGroup.command(name="treble", description="veraendere den treble")  
    async def treble(self, interaction: discord.interactions, bass: float):
        try:
            treble_float = self.convert_to_float(bass)            
            # Überprüfe, ob der Wert im gültigen Bereich liegt
            if 0.0 <= treble_float <= 3.0:
                await self.player.change_volume(treble_float)  # Lautstärke ändern
                await interaction.response.send_message(f"treble changed to {treble_float}", ephemeral=True)
            else:
                await interaction.response.send_message("treble must be between 0 and 3.", ephemeral=True)
        except ValueError as e:
            logger.error(str(e))
            await interaction.response.send_message("Wert muss Zwischen 0.01 und 3.0 sein", ephemeral=True)
        
    @MusicGroup.command(name="nodupe", description="Entfernt alle Duplikate")
    async def nodupe(self, interaction: discord.interactions):
        print()
        await interaction.response.send_message("Duplikate Entfernt", ephemeral=True)
        
    @MusicGroup.command(name="resetpl", description="setzt alle Playlist settings auf Default")
    async def resetplsettings(self, interaction: discord.interactions):
        print()
        await interaction.response.send_message("Playlistsettings reseted", ephemeral=True)
  
    @MusicGroup.command(name="back", description="Springt um 1 ind er PLaylist zurück")
    async def back(self, interaction: discord.interactions):
        print()
        await interaction.response.send_message("zurück gesprungen", ephemeral=True)
        
    @MusicGroup.command(name="sktipto", description="skipt zu einem Song")
    async def skipto(self, interaction: discord.interactions):
        print()
        await interaction.response.send_message("zu Song geskipt", ephemeral=True)
        
    @MusicGroup.command(name="plpanel", description="Erzeugt ein Queue Command Panel")
    async def plpanel(self, interaction: discord.interactions):
        print()
        await interaction.response.send_message("Panel Erzeugt", ephemeral=True)

    @MusicGroup.command(name="radio", description="lässt den Bot in ein Radio Channel Joinen")
    async def radio(self, interaction: discord.interactions):
        print()
        await interaction.response.send_message("Radio", ephemeral=True)
    
    @MusicGroup.command(name="playlist", description="Show the current playlist.")
    async def playlist(self, interaction: discord.Interaction):
        if self.player.is_empty():
            await interaction.response.send_message("The playlist is empty.", ephemeral=True)
            return

        embed_creator = PlaylistEmbed(self.player)
        embed = embed_creator.create_embed()
        buttons = embed_creator.create_buttons()

        view = discord.ui.View()
        for button in buttons:
            view.add_item(button)

        # Send the embed with buttons
        await interaction.response.send_message(embed=embed, view=view)

        # Add the button interaction handlers
        async def button_callback(interaction: discord.Interaction):
            if interaction.user != interaction.user:  # Ignoriere Interaktionen von anderen Benutzern
                return
            if interaction.custom_id == "back":
                self.player.previous_page()
            elif interaction.custom_id == "next":
                self.player.next_page()

            # Update the embed and resend the message
            embed = embed_creator.create_embed()
            await interaction.response.edit_message(embed=embed)

        # Add the button callback
        for button in buttons:
            button.callback = button_callback

async def setup(bot):
    await bot.add_cog(Music(bot))
