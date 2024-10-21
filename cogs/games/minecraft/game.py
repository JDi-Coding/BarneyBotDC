import discord
from discord import app_commands
from discord.ext import commands
from discord import Embed
from mcstatus import JavaServer
from config.settings import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)

async def mcserver_lookup(interaction: discord.Interaction, servername : str):
    try:
        port = 25565
        server = JavaServer.lookup(f"{servername}:{port}")
        status = server.status()
        players = status.players.online
        latency = status.latency
        await interaction.edit_original_response(
            content=f"The server has {players} player(s) online and replied in {latency} ms")
    except Exception as e:
        logger.info("Fehler in check_mcserver")
        logger.error(e)
        await interaction.edit_original_response(content=f"Could not find the server")