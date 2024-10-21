# bot.py
import logging.config
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

# Cogs laden
async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            #logger.info(f"Module {filename} loaded.")

###################################################################################

# Cogs neu laden
async def reload_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.unload_extension(f'cogs.{filename[:-3]}')
            await bot.load_extension(f'cogs.{filename[:-3]}')
            #logger.info(f"Module {filename} reloaded.")
###################################################################################

# Synchronisiere die App-Commands mit den Guilds
async def sync_guilds(guild_ids: list):
    try:
        total_synced = 0
        for guild_id in guild_ids:
            guild = bot.get_guild(guild_id)
            if guild is not None:
                synced = await bot.tree.sync(guild=guild)
                total_synced += len(synced)
            else:
                logger.warning(f"Guild ID {guild_id} not found!")
            logger.info(f"Commands synced: {total_synced}")
    except Exception as sync_exception:
        logger.error(f"Error in sync_guilds")
        raise sync_exception

###################################################################################

#Synchronisiert die App-Commands mit allen anderen Guilds.
async def start_sync():
    try:
        logger.info("sync Global")
        await bot.tree.sync()
        logger.info("sync Test")
        await sync_guilds(TEST_GUILD_IDS)
        logger.info("sync Premium")
        await sync_guilds(PREMIUM_GUILD_IDS)
        logger.info("sync Done")
    except Exception as start_sync_exception:
        raise start_sync_exception

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
        await load_cogs()  # Cogs laden
    except Exception as exceptions:
        logger.error(exceptions)
    logger.info(Style.BRIGHT +"Cogs Geladen")
    try:
        await start_sync()
    except Exception as exceptions:
        logger.error(exceptions)
      
    logger.info(Style.BRIGHT +"Commands mit Guilds Ge synced")
    print(" ")
    print("----------------------------")
    print(Style.BRIGHT + Fore.RED + "############################")
    print(Fore.BLUE +f'{bot.user.name} ist online!')
    print(Style.BRIGHT + Fore.RED +  "############################")
    print("----------------------------")
    print(" ")
    
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

