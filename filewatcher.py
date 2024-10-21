#filewatcher.py
import os
import asyncio
from sympy import false
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from config.settings import LOGGING_CONFIG
import logging

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('file-watcher')


class Filewatcher(FileSystemEventHandler):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Started watching for file changes...")
        self.observer = Observer()
        self.observer.schedule(self, path='./cogs', recursive=False)
        self.observer.start()

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            logger.info(f"Change detected in {event.src_path}, reloading cogs...")
            asyncio.run_coroutine_threadsafe(self.reload_cogs(), self.bot.loop)

    #Reloads the cogs
    async def reload_cogs(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.bot.unload_extension(f'cogs.{filename[:-3]}')
                await self.bot.load_extension(f'cogs.{filename[:-3]}')
                logger.info(f"Module {filename} reloaded.")
