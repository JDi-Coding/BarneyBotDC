# basic_cog.py
import discord
from discord.ext import commands

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Antwortet mit Pong und erwähnt den Benutzer.')
    async def Ping(self, ctx):
        await ctx.send(f'Pong! {ctx.author.mention}')

async def setup(bot):
    await bot.add_cog(Basic(bot))
