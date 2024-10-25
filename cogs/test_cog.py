# test_cog.py

import discord
from discord import app_commands
from discord.ext import commands
from cogs.test.test import test_function_1, test_function_2, test_function_3
from config.config import TEST_GUILD_IDS
from config.utils import has_premium_access

from loggin import Logger

import nltk
#nltk.data.path.clear()
#nltk.download('punkt_tab')


def get_support_response(flag: str) -> str:
    """Basierend auf dem Flag wird die passende Antwort erstellt."""
    if flag == "nahrung":
        return "Es sieht so aus, als hättest du ein Problem mit Lebensmitteln. Bitte beschreibe es genauer."
    elif flag == "verbindung":
        return "Es scheint ein Problem mit der Verbindung zu geben. Überprüfe bitte deine Internetverbindung."
    elif flag == "zahlung":
        return "Es scheint ein Problem mit deiner Zahlung zu geben. Bitte überprüfe deine Zahlungsinformationen."
    else:
        return "Vielen Dank für deine Anfrage! Unser Support-Team wird sich in Kürze bei dir melden."


def get_nlp_flag(problem: str) -> str:
        #nltk.download('all')
        print(nltk.data.path)
        """Eine einfache NLP-Methode, um das Problem zu analysieren und ein Flag zurückzugeben."""
        problem = problem.lower()
        tokens = nltk.word_tokenize(problem)  # Zerlege den Satz in Wörte
        # Einfache Schlüsselwortbasierte Erkennung (dies kann später durch komplexere Modelle ersetzt werden)
        if any(word in tokens for word in ["essen", "trinken", "nahrung", "lebensmittel"]):
            return "nahrung"
        elif any(word in tokens for word in ["internet", "verbindung", "server", "netzwerk"]):
            return "verbindung"
        elif any(word in tokens for word in ["zahlung", "rechnung", "kreditkarte", "paypal"]):
            return "zahlung"
        else:
            return "unbekannt"


class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = Logger('test').getLogger()
        self.log.info('TestCog initialized')


    TestGroup = app_commands.Group(name="test", description="Hilfe für den Bot", guild_ids=TEST_GUILD_IDS)

    @TestGroup.command(name="testasync", description="Führe Testfunktion 0 aus. async")
    async def test_command_0(self, interaction: discord.Interaction):
        asyncron = await test_function_1()
        self.log.info("test_command_0 executed")
        await interaction.response.send_message(f"Test 0: {asyncron}")

    @TestGroup.command(name="testsync", description="Führe Testfunktion 1 aus. sync")
    async def test_command_1(self, interaction: discord.Interaction):
        syncron = test_function_2()
        await interaction.response.send_message(f"Test 1: {syncron}")

    # Test-Command nur für Test-Guilds
    @TestGroup.command(name="testtestguild", description="Führe Testfunktion 2 aus.")
    async def test_command_2(self, interaction: discord.Interaction):
        await interaction.response.send_message("Test 2 wurde erfolgreich ausgeführt!")

    # Premium-Command, das auch für Test-Server verfügbar ist
    @TestGroup.command(name="testpremium", description="Premium-Funktion für Premium- und Test-Guilds. testfunktion  3")
    async def test_command_3(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if has_premium_access(guild_id):
            await interaction.response.send_message("Du hast Zugriff auf dieses Premium-Feature!")
        else:
            await interaction.response.send_message("Dieses Feature ist nur für Premium-Nutzer verfügbar.", ephemeral=True)
    
    # Globaler Command, für alle zugänglich
    @TestGroup.command(name="testglobal", description="Dieser Befehl ist für alle Nutzer verfügbar. testfunktion 4")
    async def test_command_4(self, interaction: discord.Interaction):
        await interaction.response.send_message("Globaler Befehl wurde erfolgreich ausgeführt!")
    
    # Administrator-Command nur für Administratoren
    @commands.has_permissions(administrator=True)
    @TestGroup.command(name="testadmin", description="Nur Administratoren können diesen Test ausführen. test function 5")
    async def test_command_5(self, interaction: discord.Interaction):
        await interaction.response.send_message("Dieser Befehl kann nur von Administratoren ausgeführt werden.")
    
    @TestGroup.command(name="embedtest", description="embedtest test function 6")
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
       
    @TestGroup.command(name="testlog", description="testet die logs des bots")
    async def test_command_7(self, interaction: discord.Interaction):
        try:
            self.log.debug("Debug")
            self.log.info("Info")
            self.log.warning("Warning")
            self.log.error("Error")
            self.log.critical("CRITICAL")

            await interaction.response.send_message("ERFOLGREICH")
        except Exception as e:
           await interaction.response.send_message(str(e))                
    # Test-Command als TextCommand für Test- und Premium-Guilds

    @TestGroup.command(name="foldertest", description="folder test")
    async def test_command_8(self, interaction: discord.Interaction):
        foldertest = test_function_3()
        await interaction.response.send_message(f"Test 3: {foldertest}")

    def generate_response(self, flag: str) -> str:
        # Basierend auf dem Flag eine Antwort erzeugen
        if flag == "Nahrung":
            return "Es sieht nach einem Problem im Bereich Nahrung oder Bestellung aus. Kann ich Ihnen bei einer Essensbestellung helfen?"
        elif flag == "Verbindung":
            return "Es scheint ein Problem mit der Internetverbindung zu geben. Bitte überprüfe deine Verbindung oder unseren Serverstatus."
        elif flag == "Zahlung":
            return "Es gibt ein Problem mit der Zahlung. Bitte überprüfe deine Zahlungsinformationen oder kontaktiere den Support."
        else:
            return "Vielen Dank für deine Anfrage! Unser Support-Team wird sich in Kürze bei dir melden."

    # Bot Setup

    @commands.command()
    async def test_text_1(self, ctx):
        guild_id = ctx.guild.id
        if has_premium_access(guild_id):
            await ctx.send("Du hast Zugriff auf das Premium-Text-Feature!")
        else:
            await ctx.send("Dieses Feature ist nur für Premium-Server verfügbar.")


async def setup(bot):
    await bot.add_cog(TestCog(bot))
