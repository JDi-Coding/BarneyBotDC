import discord
from discord import app_commands
from discord.ext import commands
from discord import Embed
from mcstatus import JavaServer

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
        print(e)
        await interaction.edit_original_response(content=f"Could not find the server")