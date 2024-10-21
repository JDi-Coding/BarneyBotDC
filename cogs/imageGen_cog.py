from fileinput import filename
#from PIL import Image
import os
import random
import discord
from discord.ext import commands
from discord import app_commands
import logging
from cogs.imageGen.generateImage import ImageGen
from config.settings import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('image-gen')


from diffusers import StableDiffusionPipeline
import torch
from safetensors.torch import load_file


class GenImage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    gen = app_commands.Group(name="gen", description="group for generating stuff")

    @gen.command(name="image", description="generate an image")
    @app_commands.choices(
        interference_steps=[
            app_commands.Choice(name="10", value=10),
            app_commands.Choice(name="20", value=20),
            app_commands.Choice(name="30", value=30),
            app_commands.Choice(name="40", value=40),
        ]
    )
    @app_commands.choices(
        guidance_scale=[
            app_commands.Choice(name="3", value=3),
            app_commands.Choice(name="4", value=4),
            app_commands.Choice(name="5", value=5),
            app_commands.Choice(name="6", value=6),
            app_commands.Choice(name="7", value=7),
            app_commands.Choice(name="8", value=8),
            app_commands.Choice(name="9", value=9),
            app_commands.Choice(name="10", value=10),
        ]
    )
    async def genimage(self,
                       interaction: discord.Interaction,
                       prompt: str,
                       interference_steps: int = 30,
                       guidance_scale: int = 5,
                       negative_prompt: str = "",
                       seed: int = random.randint(1, 999999),
                       ):
        await interaction.response.defer()
        try:
            imagegen = ImageGen(prompt, interference_steps, guidance_scale, negative_prompt, seed)
            image = imagegen.generate()
            imagepath = imagegen.saveimage(image=image)
            if negative_prompt == "":
                negative_prompt = "None"

            embed = discord.Embed(title="Generated Picture", color=discord.Color.blue())
            embed.add_field(name="Prompt", value=f"`Prompt:` **{prompt}**", inline=False)
            embed.add_field(name="Negativ-Prompt", value=f"`Negative prompt:` **{negative_prompt}**", inline=False)
            embed.add_field(name="Settings", value=f"`Interference_steps:` **{interference_steps}**  ,  `Guidance_scale:` **{guidance_scale}**", inline=False)
            embed.add_field(name="Seed", value=f"`Seed:` **{seed}**", inline=False)
            file = discord.File(imagepath, filename="my_image.png")
            embed.set_image(url=f"attachment://my_image.png")
            await interaction.edit_original_response(embed=embed, attachments=[file])
            os.remove(imagepath)
        except Exception as e:
            logger.error(f"Error in def genimage: {e}")



async def setup(bot):
    await bot.add_cog(GenImage(bot))