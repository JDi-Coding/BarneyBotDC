import discord
from click import prompt
from discord import app_commands
from discord.ext import commands
from discord import Embed
from fileinput import filename
#from PIL import Image
import os
import logging

from transformers.models.paligemma.convert_paligemma_weights_to_hf import device

from cogs.imageGen.device import Device

logger = logging.getLogger()
from diffusers import StableDiffusionPipeline, DDIMScheduler
import torch
from safetensors.torch import load_file


class ImageGen:
    def __init__(self, user_prompt: str, interference_steps: int, guidance_scale: int, negative_prompt: str, seed: int):
        self.prompt = user_prompt
        self.interference_steps = interference_steps
        self.guidance_scale = float(guidance_scale)
        self.height = 600
        self.width = 600
        self.negative_prompt = negative_prompt
        self.seed = seed
        self.device = Device().currentdevice
        self.folder_path = 'E:/Projekte/discordprojects/BarneyBotDC/data/generated'
        self.file_name = 'my_image.png'
        self.full_path = os.path.join(self.folder_path, self.file_name)


    #This Function Generates an Image via stable-diffusion-v1-4 and Returns the image
    def generate(self):
        # Lade die StableDiffusion Pipeline mit den gewünschten Optionen
        pipe = StableDiffusionPipeline.from_pretrained(
            "CompVis/stable-diffusion-v1-4",
            torch_dtype=torch.float16,
            safety_checker=None,
            revision='fp16'
        )
        #does not have DDMIN so not in use
        # Wähle den DDIM-Scheduler oder einen anderen
        #pipe.scheduler = DDIMScheduler.from_pretrained("CompVis/stable-diffusion-v1-4")

        # Setze die Pipeline auf das richtige Gerät (GPU oder CPU)
        pipe = pipe.to(self.device)
        # Seed für Reproduzierbarkeit
        generator = torch.manual_seed(self.seed)

        # Verwende das Modell, um ein Bild zu generieren, mit mehr Kontrolle
        image = pipe(
            self.prompt,
            num_inference_steps=self.interference_steps,  # Anzahl der Generierungsschritte
            guidance_scale=self.guidance_scale,  # Classifier-Free Guidance
            height=self.height,  # Bildhöhe
            width=self.width,  # Bildbreite
            eta=0.0,  # Steuerung des DDIM Samplers
            negative_prompt=self.negative_prompt,  # Negative Prompt, um bestimmte Ergebnisse zu vermeiden
            generator=generator  # Seed für Reproduzierbarkeit
        ).images[0]

        return image
    #This Function saving the Image Localy and Returning the Path
    def saveimage(self, image):
        if os.path.exists(self.folder_path and self.file_name != ""):
            # Speichere das Bild
            image.save(self.full_path)
            logger.info(f"Saved image to {self.full_path}")
        else:
            logger.error("path could not be found")
            return 'Error'

        if os.path.exists(self.full_path):
            #Speichere das Bild
            logger.info(f"send Image {self.full_path}")
            logger.info(f"Delete local image {self.full_path}")
            #
            return self.full_path

        else:
            logger.error("image or path could not be found")
            return 'Error'



