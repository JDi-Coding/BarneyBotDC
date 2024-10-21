import logging
import os
#from config.settings import LOGGING_CONFIG
#logging.config.dictConfig(LOGGING_CONFIG)
from discord.ext import commands


def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Das Format der Logs, die im logs-Ordner gespeichert werden
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Liste der Logger-Namen, die für bot.log konfiguriert werden sollen
    loggers = [
        'bot', 'test', 'basic', 'logging', 'memes', 'file-watcher', 'music',
        'player', 'playlist_embed', 'tempvoice', 'voice', 'help', 'startup',
        'discord', 'minecraft', 'image-gen', 'tts'
    ]

    # Alle Logger mit FileHandler versehen
    # FileHandler für alle Logs (bot.log)
    file_handler_all = logging.FileHandler('logs/bot.log')
    file_handler_all.setFormatter(formatter)
    for Info_logger in loggers:
        logger = logging.getLogger(Info_logger)
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler_all)

    # Logger für Fehler konfigurieren (error.log)
    # FileHandler für Fehler (error.log)
    file_handler_errors = logging.FileHandler('logs/error.log')
    file_handler_errors.setFormatter(formatter)
    for error_logger in loggers:
        error_logger = logging.getLogger(error_logger)
        error_logger.setLevel(logging.ERROR)
        error_logger.addHandler(file_handler_errors)

    # Logger für das Logging-System konfigurieren (log.log)
    # FileHandler für das Logging-System (log.log)
    file_handler_info = logging.FileHandler('logs/log.log')
    file_handler_info.setFormatter(formatter)
    info_logger = logging.getLogger('info')
    info_logger.setLevel(logging.INFO)
    info_logger.addHandler(file_handler_info)

    # Log-Nachricht, dass das Logging-System initialisiert wurde
    info_logger.info('Logging system initialized')


class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        #setup_logging()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        logging.getLogger('bot').error(f'Fehler bei Befehl {ctx.command}: {error}')
        await ctx.send('Ein Fehler ist aufgetreten.')
        await ctx.send('Vielleicht falschgeschrieben? Versuche !!help')


async def setup(bot):
    await bot.add_cog(LoggingCog(bot))
