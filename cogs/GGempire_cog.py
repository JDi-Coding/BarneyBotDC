from array import array
from datetime import datetime

import mysql.connector
import discord
from discord import app_commands
from discord.ext import commands
from discord import Embed
# Konfigurationsparameter für die Datenbankverbindung
from config.config import db_host, db_port, db_user, db_password, dbname

from cogs.games.good_game_empire.game import *


class GGEmpire(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Definiere die Gruppe für die Slash-Befehle
    gg_group = app_commands.Group(name="gg", description="gg commands")

    @gg_group.command(name="add_member", description="Füge ein Mitglied zur Allianz hinzu")
    async def add_member(self, interaction: discord.Interaction, member: discord.Member, ingame_name: str):
        add_member_result = await add_member_to_alliance(interaction, member, ingame_name)

    @gg_group.command(name="addplace", description="Füge einen Platz hinzu")
    @app_commands.choices(
        place_type=[
            app_commands.Choice(name="Hauptburg", value="Hauptburg"),
            app_commands.Choice(name="Außenposten", value="Außenposten"),
            app_commands.Choice(name="Hauptstädte", value="Hauptstädte"),
            app_commands.Choice(name="Handelsmetropolen", value="Handelsmetropolen"),
            app_commands.Choice(name="Königstürme", value="Königstürme"),
            app_commands.Choice(name="Monumente", value="Monumente"),
            app_commands.Choice(name="Ressourcen Dörfer", value="Ressourcen Dörfer"),
        ]
    )
    @app_commands.choices(
        world_name=[
            app_commands.Choice(name="Das Große Imperium", value="Das Große Imperium"),
            app_commands.Choice(name="Immerwinter-Gletscher", value="Immerwinter-Gletscher"),
            app_commands.Choice(name="Brennende Sande", value="Brennende Sande"),
            app_commands.Choice(name="Die Feuergipfel", value="Die Feuergipfel"),
            app_commands.Choice(name="Schlacht um Berimond", value="Schlacht um Berimond"),
            app_commands.Choice(name="Sturminseln", value="Sturminseln"),
            app_commands.Choice(name="Die Außenwelten", value="Die Außenwelten"),
        ]
    )
    async def add_place(self, interaction: discord.Interaction, place_type: str, place_name: str, coords: str, world_name: str):
        interaction.response.send_message(f"Wird hinzugefeügt")
        add_place = await add_place_to_member(interaction, place_type, place_name, coords, world_name)

    @gg_group.command(name="remove_member", description="Entferne ein Mitglied aus der Allianz")
    async def remove_member(self, interaction: discord.Interaction, member: discord.Member):
        add_member_result = await remove_member_from_alliance(interaction, member)

    @gg_group.command(name="removeplace", description="Entferne einen Platz")
    @app_commands.choices(
        world_name=[
            app_commands.Choice(name="Das Große Imperium", value="Das Große Imperium"),
            app_commands.Choice(name="Immerwinter-Gletscher", value="Immerwinter-Gletscher"),
            app_commands.Choice(name="Brennende Sande", value="Brennende Sande"),
            app_commands.Choice(name="Die Feuergipfel", value="Die Feuergipfel"),
            app_commands.Choice(name="Schlacht um Berimond", value="Schlacht um Berimond"),
            app_commands.Choice(name="Sturminseln", value="Sturminseln"),
            app_commands.Choice(name="Die Außenwelten", value="Die Außenwelten"),
        ]
    )
    async def remove_place(self, interaction: discord.Interaction, place_name: str, world_name: str):
        interaction.response.send_message(f"Wird entfernt")
        remove_place_result = await remove_place_from_member(interaction, place_name, world_name)
    @gg_group.command(name="show_member", description="Zeige alle Mitglieder der Allianz an")
    async def show_member(self, interaction: discord.Interaction):
        alliance_members = await show_members_of_allience(interaction)

    @gg_group.command(name="repattack", description="Melde einen Angriff")
    @app_commands.choices(
        world=[
            app_commands.Choice(name="Das Große Imperium", value="Das Große Imperium"),
            app_commands.Choice(name="Immerwinter-Gletscher", value="Immerwinter-Gletscher"),
            app_commands.Choice(name="Brennende Sande", value="Brennende Sande"),
            app_commands.Choice(name="Die Feuergipfel", value="Die Feuergipfel"),
            app_commands.Choice(name="Schlacht um Berimond", value="Schlacht um Berimond"),
            app_commands.Choice(name="Sturminseln", value="Sturminseln"),
            app_commands.Choice(name="Die Außenwelten", value="Die Außenwelten"),
        ]
    )
    async def report_attack(self, interaction: discord.Interaction, world: str, defender_name: str, coords_defender: str,attacker_name: str, coords_attacker: str, alliance_attacker: str, time_until_arrival: str):
        result_report_attack = await report_attack(interaction, world, defender_name, coords_defender, attacker_name,coords_attacker, alliance_attacker, time_until_arrival)



# Setup Funktion für den Cog
async def setup(bot: commands.Bot):
    await bot.add_cog(GGEmpire(bot))
