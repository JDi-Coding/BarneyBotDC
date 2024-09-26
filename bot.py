# bot.py
import discord
from discord.ext import commands
from discord import app_commands

import os
import logging
import asyncio
from colorama import Fore, Back, Style, init
from gtts import gTTS
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config.config import TOKEN, COMMAND_PREFIX, PREMIUM_GUILD_IDS, TEST_GUILD_IDS  # GUILD_ID importieren
from config.settings import LOGGING_CONFIG
import logging.config
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
observer = Observer()

###################################################################################

# Datei-Änderungsereignisse
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            #logger.info(f"Change detected in {event.src_path}, reloading cogs...")
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

#Synchronisiert Globale App-Commands
async def sync_global():
        synced = await bot.tree.sync()
        #logger.info(f"Synced {len(synced)} Global Command(s)")
        return len(synced)

###################################################################################

#Syncroniesiert App-Commands für die Test_Guilds
async def sync_test_guilds():
    total_synced = 0
    for TEST_GUILD_ID in TEST_GUILD_IDS:
        guild = bot.get_guild(TEST_GUILD_ID)
        if guild is not None:
            synced = await bot.tree.sync(guild=guild)
            total_synced += len(synced)
            #logger.info(f"Synced {len(synced)} Command(s) for Test Guild: {guild.name} (ID: {guild.id})")
        else:
            logger.warning(f"Test Guild ID {TEST_GUILD_ID} not found!")
    return total_synced

###################################################################################

# Synchronisiere die App-Commands mit den Premium Guilds
async def sync_premium_guilds():
    total_synced = 0
    for PREMIUM_GUILD_ID in PREMIUM_GUILD_IDS:
        guild = bot.get_guild(PREMIUM_GUILD_ID)
        if guild is not None:
            synced = await bot.tree.sync(guild=guild)
            total_synced += len(synced)
            #logger.info(f"Synced {len(synced)} Command(s) for Premium Guild {guild.name} (ID: {guild.id})")
        else:
            logger.warning(f"Premium Guild ID {PREMIUM_GUILD_ID} not found!")
    return total_synced

###################################################################################

#Synchronisiert die App-Commands mit allen anderen Guilds.
async def Start_Sync():
    global_sync_count = await sync_global()
    test_sync_count = await sync_test_guilds()
    premium_sync_count = await sync_premium_guilds()
    
    total_synced = global_sync_count + test_sync_count + premium_sync_count
    logger.info(f"Total synced {total_synced} Commands across all Guilds")

###################################################################################

# Bot starten
@bot.event
async def on_ready():
    logger.info(f'{bot.user.name} ist in den folgenden Gilden:')
    for guild in bot.guilds:
        logger.info(f'- {guild.name} (ID: {guild.id})')
    event_handler = MyHandler()  
    observer.schedule(event_handler, path='./cogs', recursive=False)
    observer.start()
    logger.info("Started watching for file changes...")
    try:
        await load_cogs()  # Cogs laden
    except Exception as e:
        logger.error(e)
    logger.info(Style.BRIGHT +"Cogs Geladen")
    try:
        await Start_Sync()
    except Exception as e:
        logger.error(e)
      
    logger.info(Style.BRIGHT +"Commands mit Guilds Gesynced")
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
        ctx.voice_client.play(discord.FFmpegPCMAudio("tts.mp3"), after=lambda e: os.remove("tts.mp3"))
    else:
        await ctx.send("I need to be in a voice channel to speak.")
###################################################################################

try:
    bot.run(TOKEN)
except Exception as e:
    logger.error(f"ERROR Bot konnte nicht gestartet werden: {e}")
finally:
    observer.stop()
    observer.join()
