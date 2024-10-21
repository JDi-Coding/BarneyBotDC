#startup.py
import discord
from discord.ext import commands
from gtts import gTTS
import os
import sys
from config.config import PREMIUM_GUILD_IDS, TEST_GUILD_IDS
from colorama import Fore, Style, init

sys.stdout.reconfigure(encoding='utf-8')
init(autoreset=True)

class Startup:
    def __init__(self, bot):
        self.bot = bot
        from loggin import Logger
        self.log = Logger('startup').getLogger()
    #Starte die Notwendigen funktionen
    async def run(self):
        await self.load_cogs()
        await self.start_sync()
        await self.startup_getguilds_message()
        await self.startup_message()


    #Lade die cog dateien
    async def load_cogs(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.bot.load_extension(f'cogs.{filename[:-3]}')
                self.log.info(f"Module {filename} loaded.")

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
                    self.log.warning(f"Guild ID {guild_id} not found!")
                #self.log.info(f"Commands synced: {total_synced}")
        except Exception as sync_exception:
            self.log.error(f"Error in sync_guilds")
            raise sync_exception

    #Synchronisiert die App-Commands mit allen anderen Guilds.
    async def start_sync(self):
        try:
            self.log.info("Starting sync")

            self.log.info("Sync Global")
            await self.bot.tree.sync()
            self.log.info("Sync Test")
            await self.sync_guilds(TEST_GUILD_IDS)
            self.log.info("Sync Premium")
            await self.sync_guilds(PREMIUM_GUILD_IDS)

            self.log.info("Finished sync")
        except Exception as start_sync_exception:
            raise start_sync_exception

    #Startup Message
    async def startup_message(self):
        print(" ")
        print("----------------------------")
        print(Style.BRIGHT + Fore.RED + "############################")
        print(Fore.BLUE + f'{self.bot.user.name} ist online!')
        print(Style.BRIGHT + Fore.RED + "############################")
        print("----------------------------")
        print(" ")

    #Zeigt in welchen Guilden, der Bot ist.
    async def startup_getguilds_message(self):
        self.log.info(f'{self.bot.user.name} ist in den folgenden Gilden:')
        for guild in self.bot.guilds:
            self.log.info(f'- {guild.name} (ID: {guild.id})')




