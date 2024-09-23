# logging_cog.py
import os
import logging
from discord.ext import commands

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.setup_logging()

    def setup_logging(self):
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

        # Logger für allgemeine Infos (log.log)
        info_logger = logging.getLogger('info')
        info_logger.setLevel(logging.INFO)
        file_handler_info = logging.FileHandler('logs/log.log')
        file_handler_info.setFormatter(formatter)
        info_logger.addHandler(file_handler_info)

        bot_logger.info('Logging system initialized')
        info_logger.info('Logging system initialized')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        logging.getLogger('error').error(f'Fehler bei Befehl {ctx.command}: {error}')
        await ctx.send('Ein Fehler ist aufgetreten.')

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))
