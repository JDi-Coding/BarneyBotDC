# logging_cog.py
import logging
import os

from config.settings import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)
from discord.ext import commands
from discord import app_commands
def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    #Das Format der Logs die im logs Ordner gespeichert werden
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #Example: 2024-09-26 19:00:49,406 - info - INFO - Logging system initialized

    file_handler_all = logging.FileHandler('logs/bot.log')
    file_handler_all.setFormatter(formatter)

    # Logger für alle Logs (bot.log)
    bot_logger = logging.getLogger('bot')
    test_logger = logging.getLogger('test')
    basic_logger = logging.getLogger('basic')
    logging_logger = logging.getLogger('logging')
    memes_logger = logging.getLogger('memes')
    file_watcher_logger = logging.getLogger('file-watcher')
    music_logger = logging.getLogger('music')
    player_logger = logging.getLogger('player')
    playlist_embed_logger = logging.getLogger('playlist_embed')
    tempvoice_logger = logging.getLogger('tempvoice')
    voice_logger = logging.getLogger('voice')
    help_logger = logging.getLogger('help')
    startup_logger = logging.getLogger('startup')
    discord_logger = logging.getLogger('discord')
    minecraft_logger = logging.getLogger('minecraft')
    image_gen_logger = logging.getLogger('image-gen')
    tts_logger = logging.getLogger('tts')


    bot_logger.setLevel(logging.DEBUG)

    bot_logger.addHandler(file_handler_all)
    test_logger.addHandler(file_handler_all)
    basic_logger.addHandler(file_handler_all)
    logging_logger.addHandler(file_handler_all)
    memes_logger.addHandler(file_handler_all)
    file_watcher_logger.addHandler(file_handler_all)
    music_logger.addHandler(file_handler_all)
    player_logger.addHandler(file_handler_all)
    playlist_embed_logger.addHandler(file_handler_all)
    tempvoice_logger.addHandler(file_handler_all)
    voice_logger.addHandler(file_handler_all)
    help_logger.addHandler(file_handler_all)
    startup_logger.addHandler(file_handler_all)
    discord_logger.addHandler(file_handler_all)
    minecraft_logger.addHandler(file_handler_all)
    image_gen_logger.addHandler(file_handler_all)
    tts_logger.addHandler(file_handler_all)

    # Logger für Fehler (error.log)
    error_logger = logging.getLogger('error')
    error_logger.setLevel(logging.WARNING)
    file_handler_errors = logging.FileHandler('logs/error.log')
    file_handler_errors.setFormatter(formatter)
    error_logger.addHandler(file_handler_errors)

    # Logger für das logging system (log.log)
    # speichert alle Logs für das loggin system hier.
    info_logger = logging.getLogger('info')
    info_logger.setLevel(logging.INFO)
    file_handler_info = logging.FileHandler('logs/log.log')
    file_handler_info.setFormatter(formatter)
    info_logger.addHandler(file_handler_info)

    info_logger.info('Logging system initialized')


class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        setup_logging()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        logging.getLogger('bot').error(f'Fehler bei Befehl {ctx.command}: {error}')
        await ctx.send('Ein Fehler istadawd aufgetreten.')
        await ctx.send('Command Vielleicht falschgeschrieben versuche !!help')

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))
