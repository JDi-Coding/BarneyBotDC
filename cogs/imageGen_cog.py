from fileinput import filename
#from PIL import Image
import os

import discord
from discord.ext import commands
from discord import app_commands
import logging
from cogs.imageGen.generateImage import ImageGen
from config.settings import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('bot')


from diffusers import StableDiffusionPipeline
import torch
from safetensors.torch import load_file


class GenImage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    gen = app_commands.Group(name="gen", description="group for generating stuff")

    @gen.command(name="image", description="generate an image")
    async def genimage(self, interaction: discord.Interaction,
                       prompt: str, interference_steps: int,
                       guidance_scale: int, negative_prompt: str,
                       seed: int):
        await interaction.response.defer(ephemeral=True)

        imagegen = ImageGen(prompt, interference_steps, guidance_scale, negative_prompt, seed)
        image = imagegen.generate()
        imagepath = imagegen.saveimage(image=image)
        await interaction.delete_original_response()

        embed = discord.Embed(title="Generated Picture", color=discord.Color.blue())
        embed.add_field(name="Prompt", value=f"`Prompt:` **{prompt}**", inline=False)
        embed.add_field(name="Negativ-Prompt", value=f"`Negative prompt:` **{negative_prompt}**", inline=False)
        embed.add_field(name="Settings", value=f"`Interference_steps:` **{interference_steps}**  ,  `Guidance_scale:` **{guidance_scale}**", inline=False)
        embed.add_field(name="Seed", value=f"`Seed:` **{seed}**", inline=False)
        file = discord.File(imagepath, filename="my_image.png")
        embed.set_image(url=f"attachment://my_image.png")
        await interaction.followup.send(embed=embed, file=file)
        os.remove(imagepath)



async def setup(bot):
    await bot.add_cog(GenImage(bot))