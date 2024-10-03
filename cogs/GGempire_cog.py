from array import array
from datetime import datetime

import mysql.connector
import discord
from discord import app_commands
from discord.ext import commands
from discord import Embed
# Konfigurationsparameter für die Datenbankverbindung
from config.config import db_host, db_port, db_user, db_password, dbname


class GGEmpire(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Definiere die Gruppe für die Slash-Befehle
    gg_group = app_commands.Group(name="gg", description="gg commands")

    @gg_group.command(name="add_member", description="Füge ein Mitglied zur Allianz hinzu")
    async def add_member(self, interaction: discord.Interaction, member: discord.Member, ingame_name: str):
        guild_id = interaction.guild.id  # Die GUILD ID des Servers abrufen

        # Verbinde zur Datenbank
        conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=dbname
        )
        cursor = conn.cursor()
        # Hole die Allianz-ID basierend auf der GUILD ID
        cursor.execute('SELECT id, name FROM alliances WHERE dc_guild_ID = %s', (str(guild_id),))
        result = cursor.fetchone()
        if result:
            # Wenn die Allianz existiert, verwende die ID und den Namen
            alliance_id = result[0]
            alliance_name = result[1]
        else:
            # Erstelle eine neue Allianz, wenn sie nicht existiert
            cursor.execute('''
            INSERT INTO alliances (name, dc_guild_ID) VALUES (%s, %s)
            ''', (interaction.guild.name, str(guild_id)))
            conn.commit()

            # Hole die neu erstellte Allianz-ID
            cursor.execute('SELECT LAST_INSERT_ID()')
            alliance_id = cursor.fetchone()[0]
            alliance_name = interaction.guild.name  # Setze den Namen auf den Servernamen
            await interaction.response.send_message(f"Neue Allianz '{alliance_name}' mit ID {alliance_id} erstellt.")
        # Hole die Discord-ID des Mitglieds
        dc_user_id = member.id
        dc_name = member.name
        # Überprüfen, ob der Spieler bereits in der DB vorhanden ist
        cursor.execute('SELECT * FROM players WHERE dc_user_ID = %s', (dc_user_id,))
        player_result = cursor.fetchone()
        if player_result:
            await interaction.response.send_message(f"{dc_name} ist bereits in der Datenbank registriert.")
        else:
            # Füge den Spieler zur Tabelle hinzu, wenn er nicht existiert
            cursor.execute('''
            INSERT INTO players (dc_user_ID, dc_name, ingame_name) VALUES (%s, %s, %s)
            ''', (dc_user_id, dc_name, ingame_name))
            conn.commit()
            # Füge das Mitglied zur Allianz hinzu
        cursor.execute('''
                    INSERT INTO alliances_members_kt (dc_user_ID, allience_ID) VALUES (%s,%s)
                    ''', (dc_user_id, alliance_id,))
        conn.commit()
        await interaction.response.send_message(f"{dc_name} wurde der Allianz '{alliance_name}' hinzugefügt.")
        cursor.close()
        conn.close()

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
        # Hole die Allianz-ID basierend auf der GUILD ID
        guild_id = interaction.guild.id
        user_id = interaction.user.id
        user_name = interaction.user.name
        userarray = [user_id, user_name]


        conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=dbname
        )
        cursor = conn.cursor()
        # Hole die Allianz-ID
        cursor.execute('SELECT id FROM alliances WHERE dc_guild_ID = %s', (str(guild_id),))
        allianz_result = cursor.fetchone()
        if allianz_result:
            alliance_id = allianz_result[0]
            # Hole die Welt-ID basierend auf dem Welt-Namen
            cursor.execute('SELECT id FROM world WHERE world_name = %s', (world_name,))
            world_result = cursor.fetchone()
            if not world_result:
                await interaction.response.send_message(f"Die Welt '{world_name}' existiert nicht.")
                return
            world_id = world_result[0]
            cursor.execute('SELECT id FROM place_type WHERE type = %s', (str(place_type),))
            place_type_result = cursor.fetchone()
            if not place_type_result:
                await interaction.response.send_message(f"{place_type} existiert nicht.")
                return
            place_type_id = place_type_result[0]

            cursor.execute('SELECT ingame_name FROM players WHERE dc_user_ID = %s',
                           (userarray[0],))
            ingame_name_result = cursor.fetchone()
            if not ingame_name_result:
                await interaction.response.send_message(f"{user_name} existiert nicht.")
                return
            ingame_name = ingame_name_result[0]
            # Überprüfen, ob der Platzname bereits existiert
            cursor.execute('SELECT * FROM coordinates_player_place WHERE place_name = %s AND world_id = %s',
                           (place_name, world_id))
            place_exists = cursor.fetchone()
            if place_exists:
                await interaction.response.send_message(
                    f"Der Platz '{place_name}' existiert bereits in der Welt {world_name}.")
                return
            # Teile die Koordinaten auf
            try:
                x, y = map(float, coords.split(";"))
            except ValueError:
                await interaction.response.send_message("Die Koordinaten müssen im Format 'x;y' angegeben werden.")
                return

            # Überprüfen, ob die Koordinaten im zulässigen Bereich liegen
            if not (-10000 <= x <= 10000) or not (-10000 <= y <= 10000):
                await interaction.response.send_message("Die Koordinaten müssen zwischen -10.000 und +10.000 liegen.")
                return

            # Füge den Platz zur Tabelle coordinates_player_place hinzu
            coordinates_player_place_id= ''
            cursor.execute('''
            INSERT INTO coordinates_player_place (id, player_name, world_id, place_id, place_name, x_coordinate, y_coordinate) VALUES (%s,%s,%s,%s,%s,%s,%s)
            ''', (coordinates_player_place_id, ingame_name, world_id, place_type_id, place_name, x, y))
            conn.commit()
            await interaction.response.send_message(
                f"{place_name} wurde hinzugefügt mit Koordinaten ({x}, {y}) in der Welt {world_name} für : {user_name}.")
        else:
            await interaction.response.send_message("Allianz nicht gefunden oder GUILD ID ungültig.")

        cursor.close()
        conn.close()

    @gg_group.command(name="remove_member", description="Entferne ein Mitglied aus der Allianz")
    async def remove_member(self, interaction: discord.Interaction, member: discord.Member):
        guild_id = interaction.guild.id

        conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=dbname
        )
        cursor = conn.cursor()

        # Hole die Allianz-ID basierend auf der GUILD ID
        cursor.execute('SELECT id FROM alliances WHERE dc_guild_ID = %s', (str(guild_id),))
        result = cursor.fetchone()

        if result:
            alliance_id = result[0]

            # Überprüfen, ob das Mitglied existiert in der Allianz
            cursor.execute('SELECT * FROM alliances_members_kt WHERE dc_user_ID = %s AND allience_ID = %s',
                           (member.id, alliance_id))
            member_exists = cursor.fetchone()

            if not member_exists:
                await interaction.response.send_message(f"{member.name} ist kein Mitglied der Allianz.")
                cursor.close()
                conn.close()
                return

            # Entferne das Mitglied aus alliances_members_kt
            cursor.execute('''
            DELETE FROM alliances_members_kt 
            WHERE dc_user_ID = %s AND allience_ID = %s
            ''', (member.id, alliance_id))

            # Entferne alle zugehörigen Koordinaten und Plätze
            cursor.execute('''
            DELETE FROM coordinates_player_place 
            WHERE player_name = %s
            ''', (member.name,))

            # Entferne den Spieler aus der Tabelle players, falls er keine anderen Einträge hat
            cursor.execute('SELECT * FROM players WHERE dc_user_ID = %s', (member.id,))
            player_result = cursor.fetchone()
            cursor.execute('DELETE FROM players WHERE dc_user_ID = %s', (member.id,))
            conn.commit()
            await interaction.response.send_message(f"{member.name} wurde aus der Allianz entfernt.")

        cursor.close()
        conn.close()

    @gg_group.command(name="removeplace", description="Entferne einen Platz")
    async def remove_place(self, interaction: discord.Interaction, place_name: str, world_name: str):
        # Hole die Allianz-ID basierend auf der GUILD ID
        guild_id = interaction.guild.id

        conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=dbname
        )
        cursor = conn.cursor()

        # Hole die Allianz-ID
        cursor.execute('SELECT id FROM alliances WHERE dc_guild_ID = %s', (str(guild_id),))
        result = cursor.fetchone()

        if result:
            alliance_id = result[0]

            # Überprüfen, ob die Welt existiert und ihre ID holen
            cursor.execute('SELECT id FROM world WHERE world_name = %s', (world_name,))
            world_result = cursor.fetchone()
            if not world_result:
                await interaction.response.send_message(f"Die Welt '{world_name}' existiert nicht.")
                cursor.close()
                conn.close()
                return

            world_id = world_result[0]

            # Überprüfen, ob der Platz existiert
            cursor.execute('''
            SELECT * FROM coordinates_player_place 
            WHERE place_name = %s AND world_id = %s
            ''', (place_name, world_id))
            place_exists = cursor.fetchone()

            if not place_exists:
                await interaction.response.send_message(f"Der Platz '{place_name}' existiert nicht in der Welt '{world_name}'.")
            else:
                # Entferne den Platz aus coordinates_player_place
                cursor.execute('''
                DELETE FROM coordinates_player_place 
                WHERE place_name = %s AND world_id = %s
                ''', (place_name, world_id))

                # Entferne den Platz aus alliences_places_kt
                #cursor.execute('''
                #DELETE FROM alliences_places_kt
                #WHERE place_name = %s AND alliances_id = %s
                #''', (place_name, alliance_id))

                conn.commit()
                await interaction.response.send_message(f"{place_name} wurde entfernt.")
        else:
            await interaction.response.send_message("Allianz nicht gefunden oder GUILD ID ungültig.")

        cursor.close()
        conn.close()
    @gg_group.command(name="show_member", description="Zeige alle Mitglieder der Allianz an")
    async def show_member(self, interaction: discord.Interaction):
        guild = interaction.guild
        guild_id = guild.id

        conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=dbname
        )
        cursor = conn.cursor()

        # Hole die Allianz-ID basierend auf der GUILD ID
        cursor.execute('SELECT id, name FROM alliances WHERE dc_guild_ID = %s', (str(guild_id),))
        result = cursor.fetchone()

        if result:
            alliance_id = result[0]
            alliance_name = result[1]

            # Hole alle Mitglieder der Allianz und deren Plätze
            cursor.execute('''
            SELECT p.dc_name, p.ingame_name, cpp.place_name, cpp.x_coordinate, cpp.y_coordinate, w.world_name
            FROM players p
            JOIN alliances_members_kt am ON p.dc_user_ID = am.dc_user_ID
            LEFT JOIN coordinates_player_place cpp ON cpp.player_name = p.ingame_name
            LEFT JOIN world w ON cpp.world_id = w.id
            WHERE am.allience_ID = %s
            ORDER BY p.dc_name, w.world_name
            ''', (alliance_id,))
            members = cursor.fetchall()

            if members:
                # Erstelle ein Embed und füge das Guild-Logo oben rechts hinzu
                embed = Embed(title="Mitglieder der Allianz", description=f"Allianz: {alliance_name}",
                              color=discord.Color.blue())

                if guild.icon:
                    embed.set_thumbnail(url=guild.icon.url)  # Fügt das Guild-Logo als Thumbnail hinzu

                # Verarbeite die Mitglieder und deren Plätze
                current_member = None
                member_places = ""

                for member in members:
                    dc_name = member[0]
                    ingame_name = member[1]
                    place_name = member[2] or "Kein Platz"
                    x_coordinate = member[3] or "N/A"
                    y_coordinate = member[4] or "N/A"
                    world_name = member[5] or "N/A"

                    # Wenn wir bei einem neuen Mitglied sind, füge das vorherige Mitglied zum Embed hinzu
                    if current_member and current_member != dc_name:
                        embed.add_field(
                            name=f"{current_member} (Ingame: {ingame_name})",
                            value=member_places,
                            inline=False
                        )
                        member_places = ""  # Zurücksetzen für das nächste Mitglied

                    # Füge die Informationen über den Platz des aktuellen Mitglieds hinzu
                    member_places += f"**Platz:** {place_name}\n**Koordinaten:** ({x_coordinate}, {y_coordinate})\n**Welt:** {world_name}\n\n"
                    current_member = dc_name

                # Füge das letzte Mitglied hinzu
                if current_member:
                    embed.add_field(
                        name=f"{current_member} (Ingame: {ingame_name})",
                        value=member_places,
                        inline=False
                    )

                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Es gibt keine Mitglieder in dieser Allianz.")
        else:
            await interaction.response.send_message("Allianz nicht gefunden oder GUILD ID ungültig.")

        cursor.close()
        conn.close()

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
    async def report_attack(self, interaction: discord.Interaction, world: str, defender_name: str,
                            coords_defender: str,attacker_name: str,
                            coords_attacker: str, alliance_attacker: str, time_until_arrival: str):
        alliance_defender =""
        user_name = interaction.user.name
        aliance_name = interaction.guild.name
        # Teile die Koordinaten des Verteidigers auf
        try:
            defender_x, defender_y = map(float, coords_defender.split(";"))
        except ValueError:
            await interaction.response.send_message(
                "Die Koordinaten des Verteidigers müssen im Format 'x;y' angegeben werden.")
            return

        # Teile die Koordinaten des Angreifers auf
        try:
            attacker_x, attacker_y = map(float, coords_attacker.split(";"))
        except ValueError:
            await interaction.response.send_message(
                "Die Koordinaten des Angreifers müssen im Format 'x;y' angegeben werden.")
            return

        # Erstelle das Embed
        embed = discord.Embed(
            title="⚔️ Angriff gemeldet",
            description="Ein neuer Angriff wurde gemeldet!",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )

        # Wenn das Guild-Icon verfügbar ist, wird es als Thumbnail verwendet
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)

        # Verteidiger-Info hinzufügen
        embed.add_field(name="🌍 Welt", value=world, inline=False)
        embed.add_field(name="🏰 Verteidiger", value=defender_name, inline=True)
        embed.add_field(name="📍 Koordinaten des Verteidiger", value=f"({defender_x}, {defender_y})", inline=True)
        embed.add_field(name="🛡️ Allianz des Verteidiger", value=aliance_name, inline=True)

        # Angreifer-Info hinzufügen
        embed.add_field(name="⚔️ Angreifer", value=attacker_name, inline=True)
        embed.add_field(name="📍 Koordinaten des Angreifers", value=f"({attacker_x}, {attacker_y})", inline=True)
        embed.add_field(name="🏴‍☠️ Allianz des Angreifers", value=alliance_attacker, inline=True)

        # Zeit bis zur Ankunft hinzufügen
        embed.add_field(name="️ Zeit bis zur Ankunft", value=time_until_arrival, inline=False)

        # Gemeldet von
        embed.set_footer(text=f"Gemeldet von: {user_name}", icon_url=interaction.user.avatar.url)

        # Sende das Embed
        await interaction.response.send_message(embed=embed)


# Setup Funktion für den Cog
async def setup(bot: commands.Bot):
    await bot.add_cog(GGEmpire(bot))
