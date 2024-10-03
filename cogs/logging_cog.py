# logging_cog.py
import logging
import os

from config.settings import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)
from discord.ext import commands
def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Logger für alle Logs (bot.log)
    bot_logger = logging.getLogger('bot')
    bot_logger.setLevel(logging.DEBUG)
    file_handler_all = logging.FileHandler('logs/bot.log')
    file_handler_all.setFormatter(formatter)
    bot_logger.addHandler(file_handler_all)

    # Logger für Fehler (error.log)
    error_logger = logging.getLogger('error')
    error_logger.setLevel(logging.WARNING)
    file_handler_errors = logging.FileHandler('logs/error.log')
    file_handler_errors.setFormatter(formatter)
    error_logger.addHandler(file_handler_errors)

    # Logger für allgemeine Informationen (log.log)
    info_logger = logging.getLogger('info')
    info_logger.setLevel(logging.INFO)
    file_handler_info = logging.FileHandler('logs/log.log')
    file_handler_info.setFormatter(formatter)
    info_logger.addHandler(file_handler_info)

    bot_logger.info('Logging system initialized')
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
