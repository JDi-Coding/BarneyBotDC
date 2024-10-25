import spacy
import discord
from discord.ext import commands
from discord import app_commands

# Lade das deutsche Sprachmodell
nlp = spacy.load("de_core_news_sm")
user_sessions = {}

class SupportBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        from logging import Logger
        #self.log = Logger('bot').getLogger()

    @app_commands.command(name="support", description="I help you with Topics in GGEmpire")
    async def support(self, interaction: discord.Interaction, problem: str):
        user_id = interaction.user.id
        # Initialisiere die Session für den Benutzer, falls nicht vorhanden
        if user_id not in user_sessions:
            user_sessions[user_id] = {
                "topic": None,
                "step": None,
                "history": []
            }
        # Analysiere das Problem und speichere das Hauptthema in der Session
        main_topic = self.identify_topic(problem)
        user_sessions[user_id]["topic"] = main_topic
        user_sessions[user_id]["step"] = "initial"
        user_sessions[user_id]["history"].append(problem)

        # Erste Antwort, basierend auf dem identifizierten Hauptthema
        if main_topic == "Nahrung":
            response = "Um mehr Nahrung zu produzieren, gibt es verschiedene Wege, z.B. durch das Bauen von Bauernhöfen und das Upgraden von Nahrungsgebäuden. Hast du das schon probiert?"
            user_sessions[user_id]["step"] = "nahrung_suggestion"

        elif main_topic == "Truppen":
            response = "Ich sehe, dass du ein Problem mit deinen Truppen hast. Geht es um das Training oder die Verteidigung?"
            user_sessions[user_id]["step"] = "truppen_suggestion"

        else:
            response = "Kannst du mir mehr über dein Problem erzählen?"

        await interaction.response.send_message(response)

    @commands.Cog.listener()
    async def on_message(self, message):
        user_id = message.author.id
        # Überprüfe, ob der User in einer Support-Session ist und der Bot antworten soll
        if user_id in user_sessions:
            session = user_sessions[user_id]
            last_topic = session["topic"]
            session["history"].append(message.content)
            response = "_"


            # Kontextabhängige Antworten basierend auf dem letzten Thema und Fortschritt im Gespräch
            if last_topic == "Nahrung":
                if session["step"] == "nahrung_suggestion":

                    if "nein" in message.content.lower():
                        response = "Kein Problem! Um Bauernhöfe zu bauen, gehe zu deinem Bau-Menü und wähle den Bauernhof aus. Hast du genug Ressourcen für den Bau?"
                        session["step"] = "nahrung_build_help"

                    elif "ja" in message.content.lower():
                        response = "Super! Du kannst auch Außenposten erobern, die Nahrung produzieren, falls du zusätzlichen Nachschub brauchst."
                        session["step"] = "final"

                    else:
                        response = "Könntest du das nochmal genauer erklären? Ich versuche, dir bestmöglich zu helfen."

                elif session["step"] == "nahrung_build_help":

                    if "nein" in message.content.lower():
                        response = "Falls dir Ressourcen fehlen, kannst du diese auch über Handelswege oder durch Raubzüge bekommen. Du kannst auch die Öffentliche Ordnung erhöhen um mehr Nahrung zu produzieren oder mit Konstrukten diese Boosten"
                        session["step"] = "final"

                    elif "ja" in message.content.lower():
                        response = "Das ist Schön wenn du mehr Fragen hast frag mich :)"
                        session["step"] = "final"
                    else:
                        response = "tut mir leid das ich nicht verstanden bitte antworte mit Ja oder Nein"
                        session["step"] = "nahrung_build_help"

            elif last_topic == "Truppen":
                if session["step"] == "truppen_suggestion":
                    if "verteidigung" in message.content.lower():
                        response = "Für die Verteidigung kannst du Verteidigungswerkzeuge einsetzen und deine Mauern verstärken."
                        session["step"] = "truppen_defense_help"
                    elif "angriff" in message.content.lower():
                        response = "Für Angriffe kannst du offensive Einheiten trainieren und Belagerungsgeräte einsetzen."
                        session["step"] = "truppen_attack_help"
                    else:
                        response = "Kannst du mir mehr über dein Ziel mit den Truppen erzählen?"
            else:
                response = "Ich verstehe dein Problem. Gibt es noch etwas Spezielles, das du versuchst zu erreichen?"

            if session["step"] == "final":
                #Wenn der Support zu Ende ist Lösche den user aus der Support Liste
                user_sessions.pop(user_id)

            await message.channel.send(response)

    def identify_topic(self, problem: str) -> str:
        """
        Identifiziere das Thema basierend auf Schlüsselwörtern im Problem.
        """
        if "nahrung" in problem.lower() or "essen" in problem.lower():
            return "Nahrung"
        elif "truppen" in problem.lower() or "soldaten" in problem.lower():
            return "Truppen"
        # Weitere Themen...
        return "Allgemein"

async def setup(bot):
    await bot.add_cog(SupportBot(bot))
