# bot.py
# import logging
import asyncio
import logging.config
import os
import sys
import discord
from colorama import Fore, Style, init
from discord.ext import commands
from gtts import gTTS
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from config.config import TOKEN, COMMAND_PREFIX, PREMIUM_GUILD_IDS, TEST_GUILD_IDS  # GUILD_ID importieren
from config.settings import LOGGING_CONFIG

from startup import Startup

# from discord import app_commands
sys.stdout.reconfigure(encoding='utf-8')
###################################################################################
init(autoreset=True) 
# Logging konfigurieren
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('bot')

# Bot-Initialisierung
intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Observer Starten
#observer = Observer()

###################################################################################

# Datei-Änderungsereignisse
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            logger.info(f"Change detected in {event.src_path}, reloading cogs...")
            asyncio.run_coroutine_threadsafe(reload_cogs(), bot.loop)

###################################################################################

# Cogs neu laden
async def reload_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.unload_extension(f'cogs.{filename[:-3]}')
            await bot.load_extension(f'cogs.{filename[:-3]}')
            #logger.info(f"Module {filename} reloaded.")
###################################################################################

# Bot starten
@bot.event
async def on_ready():
    logger.info(f'{bot.user.name} ist in den folgenden Gilden:')
    for guild in bot.guilds:
        logger.info(f'- {guild.name} (ID: {guild.id})')

    #event_handler = MyHandler()
    #observer.schedule(event_handler, path='./cogs', recursive=False)
    #observer.start()
    #logger.info("Started watching for file changes...")

    try:
        await Startup(bot).run()
    except Exception as e:
        logger.error(f'Error in Startup: {e}')


@bot.command()
async def speak(ctx, *, text: str):
    if ctx.voice_client:
        tts = gTTS(text=text, lang='en')
        tts.save("tts.mp3")
        ctx.voice_client.play(discord.FFmpegPCMAudio("tts.mp3"), after=lambda exception: os.remove("tts.mp3"))
    else:
        await ctx.send("I need to be in a voice channel to speak.")
###################################################################################

try:
    bot.run(TOKEN)
except Exception as e:
    logger.error(f"{e}")
    logger.error(f"Bot konnte nicht gestartet werden")

