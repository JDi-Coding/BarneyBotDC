#filewatcher.py
import os
import asyncio
from sympy import false
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Filewatcher(FileSystemEventHandler):
    def __init__(self, bot):
        self.bot = bot

        self.observer = Observer()
        self.observer.schedule(self, path='./cogs', recursive=False)
        self.observer.start()
        from loggin import Logger
        self.log = Logger('download').getLogger()
        #log.info("Started watching for file changes...")

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            self.log.info(f"Change detected in {event.src_path}, reloading cogs...")
            asyncio.run_coroutine_threadsafe(self.reload_cogs(), self.bot.loop)

    #Reloads the cogs
    async def reload_cogs(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.bot.unload_extension(f'cogs.{filename[:-3]}')
                await self.bot.load_extension(f'cogs.{filename[:-3]}')
                self.log.info(f"Module {filename} reloaded.")
