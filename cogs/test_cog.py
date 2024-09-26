# test_cog.py
import discord
from discord.ext import commands
from discord import app_commands
from config.config import TEST_GUILD_IDS
from config.utils import has_premium_access
from cogs.test.test import test_function_1, test_function_2
import logging
from config.settings import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('bot')
class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="testasync", description="Führe Testfunktion 0 aus. async")
    @app_commands.guilds(*TEST_GUILD_IDS)  # Nur für erlaubte Guilds verfügbar
    async def test_command_0(self, interaction: discord.Interaction):
        asyncron = await test_function_1()
        await interaction.response.send_message(f"Test 0: {asyncron}")

    @app_commands.command(name="testsync", description="Führe Testfunktion 1 aus. sync")
    @app_commands.guilds(*TEST_GUILD_IDS)  # Nur für erlaubte Guilds verfügbar
    async def test_command_1(self, interaction: discord.Interaction):
        syncron = test_function_2()
        await interaction.response.send_message(f"Test 1: {syncron}")

    # Test-Command nur für Test-Guilds
    @app_commands.command(name="testtestguild", description="Führe Testfunktion 2 aus.")
    @app_commands.guilds(*TEST_GUILD_IDS)  # Nur für erlaubte Test-Guilds verfügbar
    async def test_command_2(self, interaction: discord.Interaction):
        await interaction.response.send_message("Test 2 wurde erfolgreich ausgeführt!")

    # Premium-Command, das auch für Test-Server verfügbar ist
    @app_commands.command(name="testpremium", description="Premium-Funktion für Premium- und Test-Guilds. testfunktion  3")
    @app_commands.guilds(*TEST_GUILD_IDS)
    async def test_command_3(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if has_premium_access(guild_id):
            await interaction.response.send_message("Du hast Zugriff auf dieses Premium-Feature!")
        else:
            await interaction.response.send_message("Dieses Feature ist nur für Premium-Nutzer verfügbar.", ephemeral=True)
    # Globaler Command, für alle zugänglich
    @app_commands.command(name="testglobal", description="Dieser Befehl ist für alle Nutzer verfügbar. testfunktion 4")
    @app_commands.guilds(*TEST_GUILD_IDS)
    async def test_command_4(self, interaction: discord.Interaction):
        await interaction.response.send_message("Globaler Befehl wurde erfolgreich ausgeführt!")

    # Administrator-Command nur für Administratoren
    @commands.has_permissions(administrator=True)
    @app_commands.command(name="testadmin", description="Nur Administratoren können diesen Test ausführen. test function 5")
    @app_commands.guilds(*TEST_GUILD_IDS)
    async def test_command_5(self, interaction: discord.Interaction):
        await interaction.response.send_message("Dieser Befehl kann nur von Administratoren ausgeführt werden.")
    
    @app_commands.command(name="embedtest", description="embedtest test function 6")
    @app_commands.guilds(*TEST_GUILD_IDS)
    async def test_command_6(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title=":notes: Das ist ein Title",
            color=discord.Color.blue()
        )
        title1 = """"Weird Al" Yankovic - Amish Paradise (Parody of "Gangsta's Paradise" by Coolio) (HD Version)"""
        title2 ="""Steve Jobs vs Bill Gates. Epic Rap Battles of History"""
        embed.set_thumbnail(url="https://www.nabu.de/imperia/md/nabu/images/arten/tiere/saeugetiere/raubtiere/hundeartige/wolf/150208-nabu-wolf-christoph-bosch21.jpeg")
        embed.add_field(
            name="FELD 1 FETT",
            value=f'[**{title1}**](https://www.youtube.com/watch?v=aknI9s01NV0)',
            inline=False
        )
        embed.add_field(
            name="FELD 2 Dünn",
            value=f"[{title2}](https://www.youtube.com/watch?v=njos57IJf-0)",
            inline=False
        )
        embed.set_footer(text=f"das ist der FOOTER")
        await interaction.response.send_message(embed=embed)
    
    # Test-Command als TextCommand für Test- und Premium-Guilds
    @commands.command()
    async def test_Text_1(self, ctx):
        guild_id = ctx.guild.id
        if has_premium_access(guild_id):
            await ctx.send("Du hast Zugriff auf das Premium-Text-Feature!")
        else:
            await ctx.send("Dieses Feature ist nur für Premium-Server verfügbar.")
    

async def setup(bot):
    await bot.add_cog(TestCog(bot))
