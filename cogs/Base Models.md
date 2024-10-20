# Cog Base
    import discord
    from discord.ext import commands
    from discord import app_commands
    import logging
    from config.settings import LOGGING_CONFIG
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger('base')
    
    class CogBase(commands.Cog):
        def __init__(self, bot):
            self.bot = bot
    
    BaseGroup = app_commands.Group(name="base", description="base")

    async def setup(bot):
        await bot.add_cog(CogBase(bot))

### das ist ein Basis Cog einfach kopieren und in eine ..."_cog.py" einfügen
# Command Help
    help="",
    description="",
    brief="",
    enabled=True, #Enables the Command or Disable the Command [TRUE/FALSE]
    hidden=False #Hids the Command for !help altough !help ping shows still information [TRUE/FALSE]
### für Text Commands
    Funktioniert nur mit ctx commands inkopatible mit app commands
# Slash Command
    @discord.app_commands.command(name="", description="", nsfw=False)
    async def (self, interaction: discord.Interaction):

### Für Slash Commands nach def den Funktionsnamen eingeben
# ffmpeg
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn -filter:a "volume=0.25, bass=g=0.0, treble=g=0.0"'
    }
### Basis ffmpeg Options
