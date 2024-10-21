#startup.py
import discord
from discord.ext import commands
from gtts import gTTS
import os
import sys
from config.config import PREMIUM_GUILD_IDS, TEST_GUILD_IDS
from colorama import Fore, Style, init
import logging.config
from config.settings import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('bot')

sys.stdout.reconfigure(encoding='utf-8')
init(autoreset=True)

class Startup:
    def __init__(self, bot):
        self.bot = bot
    #Starte die Notwendigen funktionen
    async def run(self):
        await self.load_cogs()
        await self.start_sync()
        await self.StartupMessage()

    #Lade die cog dateien
    async def load_cogs(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.bot.load_extension(f'cogs.{filename[:-3]}')
                # logger.info(f"Module {filename} loaded.")

    # Synchronisiere die App-Commands mit den Guilds
    async def sync_guilds(self, guild_ids: list):
        try:
            total_synced = 0
            for guild_id in guild_ids:
                guild = self.bot.get_guild(guild_id)
                if guild is not None:
                    synced = await self.bot.tree.sync(guild=guild)
                    total_synced += len(synced)
                else:
                    logger.warning(f"Guild ID {guild_id} not found!")
                logger.info(f"Commands synced: {total_synced}")
        except Exception as sync_exception:
            logger.error(f"Error in sync_guilds")
            raise sync_exception

    #Synchronisiert die App-Commands mit allen anderen Guilds.
    async def start_sync(self):
        try:
            logger.info("starting sync")

            logger.info("sync Global")
            await self.bot.tree.sync()
            logger.info("sync Test")
            await self.sync_guilds(TEST_GUILD_IDS)
            logger.info("sync Premium")
            await self.sync_guilds(PREMIUM_GUILD_IDS)

            logger.info("finished sync")
        except Exception as start_sync_exception:
            raise start_sync_exception

    #Startup Message
    async def StartupMessage(self):
        print(" ")
        print("----------------------------")
        print(Style.BRIGHT + Fore.RED + "############################")
        print(Fore.BLUE + f'{self.bot.user.name} ist online!')
        print(Style.BRIGHT + Fore.RED + "############################")
        print("----------------------------")
        print(" ")

    #Reloads the cogs
    async def reload_cogs(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.bot.unload_extension(f'cogs.{filename[:-3]}')
                await self.bot.load_extension(f'cogs.{filename[:-3]}')
                # logger.info(f"Module {filename} reloaded.")



