# bot.py
import discord
from discord.ext import commands
from config.config import TOKEN, COMMAND_PREFIX, PREMIUM_GUILD_IDS, TEST_GUILD_IDS  # GUILD_ID importieren
from startup import Startup
from filewatcher import Filewatcher

from loggin import Logger
log = Logger('bot').getLogger()

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
        log.error(f'Error in Filewatcher: {Filewatcher_exception}')

    try:
        await Startup(bot).run()
    except Exception as Startup_exception:
        log.error(f'Error in Startup: {Startup_exception}')


try:
    bot.run(TOKEN)
except Exception as e:
    log.error(f"{e}")
    log.error(f"Bot konnte nicht gestartet werden")
