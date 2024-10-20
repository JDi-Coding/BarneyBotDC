
# Cog
In the "name_cogs.py" files are the Discord commands declared,
which the users can use.
cog stands for: "Component Object Group"
you can look it up here -> [Cog Docs](https://cog.readthedocs.io/en/latest/)
## Cog File Structure
the File Structure is this for
Complicated Commands like music_cog.py there will be a Folder or even multiple folder 
inside cogs for better Structure

    Project-root
    ├───cogs
    │   ├───music
    │   │   ├───player
    │   │   │   └───__pycache__
## Cog-Base
This is the Base Model for all Cogs 
````Python
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
````
you can copy this and add it to a new cog file
## Commands
For the Discord Bot there are 2 Different Types of Commands
this Bot currently uses
### Text Command
With this type the Bot will react to a message send by a user

    The user send a message with a Prefix and the command name
    Example: "!ping"
    The Bot will react with pong or what you defined
    But "!piNg" will trigger an error or the Bot dont react at all

#### Declare Text Command
The Text Command can be declared like this:
````Python
    @commands.command()
        async def basic(self, ctx):
            await ctx.send("message")
````
### App Commands
With this type the Bot "tells discord which commands he can use"
and Discord shows it to the user when he types /,But Discord need to **load the commands**
you can do it like this:

````Python
    #This already automated in my Bot
    await bot.load_extension(f'cogs.{filename[:-3]}')
````
#### Declare App Command

The Base app command looks like this:

````Python
    @discord.app_commands.command(name="name-mandatory", description="desciption-mandatory")
        async def hello(self, interaction: discord.Interaction):
                await interaction.response.send_message(f"Hey {interaction.user.mention}!")
````
You can also Group these app commands this Method Will the Bot using mostly

````Python
    @basic.command(name="name-mandatory", description="desciption-mandatory")
        async def hello(self, interaction: discord.Interaction):
                await interaction.response.send_message(f"Hey {interaction.user.mention}!")
````

The App_Command Group can be declared like this:

````Python
    basic = app_commands.Group(name="basic", description="Alle Basis Commands ohne Nutzen")
````

Inside the @ Selector you can pass some flags like name, descriptions or nsfw

**Important name and description are mandatory and must be lowercase and letters**
````Python
    @basic.command(
        name="ping",
        description="Pinge den Bot an",
        nsfw=False
    )
````

