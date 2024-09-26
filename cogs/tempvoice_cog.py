# tempvoice_cog.py
import discord
from discord.ext import commands
from discord import app_commands
import logging
from config.settings import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('tempvoice')
class TempVoice(commands.Cog):
    # Speichert die IDs der temporären Channels und deren Ersteller
    def __init__(self, bot):
        self.bot = bot
        self.temp_channels = {}  # Dict mit {channel_id: member_id}, um den Ersteller zu speichern

    # Event, wenn ein Nutzer einem Voice-Channel beitritt oder verlässt
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        # Wenn der Nutzer einen Channel betritt
        if after.channel:
            # Prüfen, ob er den speziellen 'temp' Channel betritt
            logger.info(member.name + ": joined temp")
            if after.channel.name == "temp":
                # Erstelle einen temporären Channel mit dem Namen des Nutzers
                temp_channel_name = f"{member.display_name}'s room"
                temp_channel = await after.channel.clone(name=temp_channel_name)
                logger.info("Created temp_Channel: " + str(temp_channel_name) + " for: " + member.nick)
                # Setze Berechtigungen nur für den Nutzer
                await temp_channel.set_permissions(member, connect=True, manage_channels=True, manage_permissions=True)
                logger.info("Permission set for tempChannel: " + str(temp_channel_name))
                # Move den Nutzer in den neu erstellten Channel
                await member.move_to(temp_channel)
                logger.info("Moved member: " + member.name + " to TempChannel:"+ str(temp_channel_name))
                # Speichere die temporäre Channel-ID und den Ersteller
                self.temp_channels[temp_channel.id] = member.id
                logger.info("Saved TempID: " + str(temp_channel.id))

        # Wenn der Nutzer einen Channel verlässt
        if before.channel:
            # Wenn der Channel temporär ist und keine Mitglieder mehr drin sind, lösche ihn
            if before.channel.id in self.temp_channels:
                if len(before.channel.members) == 0:
                    await before.channel.delete()
                    logger.info("Deleting "+ member.nick + " temp_Channel")
                    del self.temp_channels[before.channel.id]
                    

    # Slash-Befehl zum Ändern des Channel-Namens
    @discord.app_commands.command(name="channelname", description="Ändert den Namen des temporären Voice-Channels.")
    async def channelname(self, interaction: discord.Interaction, name: str):
        # Prüfen, ob der Nutzer einen temporären Channel besitzt
        if interaction.user.voice and interaction.user.voice.channel.id in self.temp_channels:
            temp_channel = interaction.user.voice.channel
            # Prüfen, ob der Nutzer der Ersteller des Channels ist
            if self.temp_channels[temp_channel.id] == interaction.user.id:
                await temp_channel.edit(name=name)
                await interaction.response.send_message(f"Channel-Name wurde in `{name}` geändert.", ephemeral=True)
            else:
                await interaction.response.send_message("Nur der Ersteller kann den Channel anpassen.", ephemeral=True)
        else:
            await interaction.response.send_message("Du bist nicht in einem temporären Channel.", ephemeral=True)

    # Slash-Befehl zum Ändern der Bitrate des Channels
    @discord.app_commands.command(name="bitrate", description="Ändert die Bitrate des temporären Voice-Channels.")
    async def bitrate(self, interaction: discord.Interaction, bitrate: int):
        if interaction.user.voice and interaction.user.voice.channel.id in self.temp_channels:
            temp_channel = interaction.user.voice.channel
            if self.temp_channels[temp_channel.id] == interaction.user.id:
                # Prüfen, ob die Bitrate innerhalb der erlaubten Grenzen liegt
                if 8000 <= bitrate <= 96000:
                    await temp_channel.edit(bitrate=bitrate)
                    await interaction.response.send_message(f"Bitrate wurde auf `{bitrate}` geändert.", ephemeral=True)
                else:
                    await interaction.response.send_message("Die Bitrate muss zwischen 8000 und 96000 liegen.", ephemeral=True)
            else:
                await interaction.response.send_message("Nur der Ersteller kann den Channel anpassen.", ephemeral=True)
        else:
            await interaction.response.send_message("Du bist nicht in einem temporären Channel.", ephemeral=True)

    # Slash-Befehl zum Setzen der maximalen Benutzerzahl
    @discord.app_commands.command(name="maxuser", description="Ändert die maximale Benutzeranzahl im temporären Voice-Channel.")
    async def maxuser(self, interaction: discord.Interaction, max_users: int):
        if interaction.user.voice and interaction.user.voice.channel.id in self.temp_channels:
            temp_channel = interaction.user.voice.channel
            if self.temp_channels[temp_channel.id] == interaction.user.id:
                if 1 <= max_users <= 99:  # Discord erlaubt eine maximale Nutzerzahl von 99 in Voice-Channels
                    await temp_channel.edit(user_limit=max_users)
                    await interaction.response.send_message(f"Maximale Nutzeranzahl wurde auf `{max_users}` gesetzt.", ephemeral=True)
                else:
                    await interaction.response.send_message("Die maximale Nutzeranzahl muss zwischen 1 und 99 liegen.", ephemeral=True)
            else:
                await interaction.response.send_message("Nur der Ersteller kann den Channel anpassen.", ephemeral=True)
        else:
            await interaction.response.send_message("Du bist nicht in einem temporären Channel.", ephemeral=True)

    #Befehl um alle Verfügbaren SlashBefehle anzuzeigen
    @commands.command(
            help="hope it was helpfull : )",
            description="this Command Shows every Slash-Command available in this Category. usage: [Prefix][Category]info",
            brief="-> Shows every Slash-Command",
            enabled=True, #Enables the Command or Disable the Command [TRUE/FALSE]
            hidden=False #Hids the Command for !help altough !help ping shows still information [TRUE/FALSE]
    )
    async def TempVCInfo(self, ctx):
        # Alle /-Befehle des Bots
        commands_list = self.bot.tree.get_commands()
        # Filtere die Slash-Befehle, die zu dieser Klasse gehören
        meme_commands = [cmd.name for cmd in commands_list if isinstance(cmd, app_commands.Command) and cmd.binding == self]

        #Naricht mit allen Befehlen generieren
        if meme_commands:
            commands_str = "\n".join(f"/{cmd}" for cmd in meme_commands)
            await ctx.send(f"Verfügbare Temp-Slash-Befehle:\n{commands_str}")
        else:
            await ctx.send("Es gibt keine slash Befehle in dieser Kategorie")


async def setup(bot):
    await bot.add_cog(TempVoice(bot))
