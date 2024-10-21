# bot.py
# import logging
import discord
from discord.ext import commands
from config.config import TOKEN, COMMAND_PREFIX, PREMIUM_GUILD_IDS, TEST_GUILD_IDS  # GUILD_ID importieren
from config.settings import LOGGING_CONFIG
import logging.config

from startup import Startup
from filewatcher import Filewatcher

# Logging konfigurieren
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('bot')

# Bot-Initialisierung
intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Bot starten
@bot.event
async def on_ready():
    try:
        Filewatcher(bot)
    except Exception as Filewatcher_exception:
        logger.error(f'Error in Filewatcher: {Filewatcher_exception}')

    try:
        await Startup(bot).run()
    except Exception as Startup_exception:
        logger.error(f'Error in Startup: {Startup_exception}')


try:
    bot.run(TOKEN)
except Exception as e:
    logger.error(f"{e}")
    logger.error(f"Bot konnte nicht gestartet werden")

