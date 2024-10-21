import discord
from discord import app_commands
from discord.ext import commands

#from config.settings import LOGGING_CONFIG
import  logging.config
#logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('help')


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Liste von Gruppen und Cogs, die ausgeschlossen werden sollen
        self.excluded_groups = ["test", "Important", "Owner"]  # Füge hier weitere Gruppen hinzu
        self.excluded_cogs = ["TestCog", "MonitorCog", "LoggingCog", "OwnerCog"]  # Füge hier weitere Cogs hinzu
        
    HelpGroup = app_commands.Group(name="help", description="Hilfe für den Bot")
    
    @HelpGroup.command(name="commands", description="Liste aller Slash-Befehle und deren Beschreibung")
    async def commands(self, interaction: discord.Interaction):
        all_commands = await self.get_all_commands()

        if not all_commands:
            await interaction.user.send("Es gibt keine verfügbaren Befehle.")  # DM an den Nutzer
            return

        # Erstelle das Embed
        embed = discord.Embed(title="Befehle", color=discord.Color.blue())

        for group_name, commands in all_commands.items():
            commands_list = "\n".join(f"`/{name}`: {desc}" for name, desc in commands)
            embed.add_field(name=group_name, value=commands_list, inline=False)

        await interaction.user.send(embed=embed)# DM an den Nutzer
        await interaction.response.send_message("Ich habe die Befehle dir Private Geschickt")
        
    async def get_all_commands(self):
        """Holt alle Slash-Befehle aus allen Cogs und gruppiert sie nach Gruppenname."""
        commands_dict = {}
        
        # Iteriere über alle Cogs
        for cog_name, cog in self.bot.cogs.items():
            if cog_name in self.excluded_cogs:
                logger.debug(f"Überspringe Cog: {cog_name}")
                continue
            logger.debug(f"Überprüfe Cog: {cog_name}")
            
            # Prüfen, ob der Cog eine Command-Gruppe hat
            for command_group in cog.__dict__.values():
                if isinstance(command_group, app_commands.Group) and command_group.name not in self.excluded_groups:
                    for command in command_group.commands:
                        cmd = command_group.get_command(command.name)
                        if cmd:  # Sicherstellen, dass der Befehl existiert
                            commands_dict.setdefault(command_group.name, []).append((command.name, cmd.description))

            # Hole auch die Befehle ohne Gruppen
            for command in cog.get_app_commands():  # Nur App Commands
                if isinstance(command, app_commands.Command) and not isinstance(command, app_commands.Group):
                    commands_dict.setdefault(cog.__class__.__name__, []).append((command.name, command.description))

        return commands_dict

async def setup(bot):
    await bot.add_cog(Help(bot))
