# bot.py
import discord
from discord.ext import commands
from discord import app_commands

import os
import logging
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import TOKEN, COMMAND_PREFIX
from settings import LOGGING_CONFIG
import logging.config


# Logging konfigurieren
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('bot')

# Bot-Initialisierung
intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

#Observer Starten
observer = Observer()

# Cogs laden
async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            logger.info(f"Module {filename} loaded.")

# Cogs neu laden
async def reload_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.unload_extension(f'cogs.{filename[:-3]}')
            await bot.load_extension(f'cogs.{filename[:-3]}')
            logger.info(f"Module {filename} reloaded.")

# Datei-Änderungsereignisse
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            logger.info(f"Change detected in {event.src_path}, reloading cogs...")
            asyncio.run_coroutine_threadsafe(reload_cogs(), bot.loop)

# Bot starten
@bot.event
async def on_ready():
    event_handler = MyHandler()  
    observer.schedule(event_handler, path='./cogs', recursive=False)
    observer.start()
    logger.info("Started watching for file changes...")
    await load_cogs()  # Cogs laden
    logger.info("Cogs Geladen")
    try:
        tguild = discord.Object(id=911273680301084753)
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} Command(s)")
    except Exception as e:
        logger.error(e)
    print(" ")
    print("----------------------------")
    print("############################")
    print(f'{bot.user.name} ist online!')
    print("############################")
    print("----------------------------")
    print(" ")


try:
    bot.run(TOKEN)
except Exception as e:
    logger.error("ERROR Bot konnte nicht gestarted werden {e}")
finally:
    observer.stop()
    observer.join()
