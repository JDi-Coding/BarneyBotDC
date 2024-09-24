# voice_cog.py
import discord
from discord.ext import commands
from discord import app_commands
import logging.config
logger = logging.getLogger('bot')

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

async def setup(bot):
    await bot.add_cog(Voice(bot))
