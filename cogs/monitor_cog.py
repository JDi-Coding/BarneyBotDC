# cogs/monitor_cog.py
import asyncio
import logging
import os

from discord.ext import commands
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from config.settings import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('monitor')
class MyHandler(FileSystemEventHandler):
    def __init__(self, bot):
        self.bot = bot

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            logger.info(f"Change detected in {event.src_path}, reloading cogs...")
            asyncio.run_coroutine_threadsafe(self.reload_cogs(), self.bot.loop)

    async def reload_cogs(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.bot.unload_extension(f'cogs.{filename[:-3]}')
                await self.bot.load_extension(f'cogs.{filename[:-3]}')
                logger.info(f"Module {filename} reloaded.")

class MonitorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.observer = Observer()

    @commands.Cog.listener()
    async def on_ready(self):
        event_handler = MyHandler(self.bot)
        self.observer.schedule(event_handler, path='./cogs', recursive=False)
        self.observer.start()
        logger.info("Started watching for file changes...")

    def cog_unload(self):
        self.observer.stop()
        self.observer.join()
        logger.info("Stopped watching for file changes.")

async def setup(bot):
    await bot.add_cog(MonitorCog(bot))
