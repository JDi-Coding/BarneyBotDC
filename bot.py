# bot.py
import discord
from discord.ext import commands
import os
from config import TOKEN, COMMAND_PREFIX
from settings import LOGGING_CONFIG  # Importiere Logging-Konfiguration
# Stelle sicher, dass das Logging konfiguriert wird
import logging.config
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('bot')

# Bot-Initialisierung
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Cogs laden
async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f"Module {filename} loaded.")
            logger.info(f"Module {filename} loaded.")  # Logge beim Laden von Cogs

# Bot starten
@bot.event
async def on_ready():
    await load_cogs()  # Cogs laden
    logger.info("Bot ist gestartet")  # Manuelle Log-Nachricht
    print(" ")
    print("----------------------------")
    print("############################")
    print(f'{bot.user.name} ist online!')
    print("############################")
    print("----------------------------")
    print(" ")

bot.run(TOKEN)