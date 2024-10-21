import os
from logging import raiseExceptions

import yt_dlp
from imageio.plugins.ffmpeg import download
from jinja2.nodes import Import
from sympy.codegen.ast import Raise

import discord
from discord import app_commands
from discord.ext import commands
import logging
from config import settings
#logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger('bot')

class Download:
    def __init__(self, input_url: str):
        try:
            self.url = None
            self.info = None
            self.filename = None
            self.title = None
            self.download_dir = "C:/Users/jason/Downloads/ytdownload"

            if not os.path.exists(self.download_dir):
                os.makedirs(self.download_dir)

            self.ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]', #Beste Video und Audio Qualitaet
                'outtmpl': f'{self.download_dir}/%(title)s.%(ext)s', # Pfad wo das Video gespeichert wird
            }

            self.Set_Url(input_url)
            self.Download_from_Url()
        except Exception as e:
            raise e

    #Setze die Url des Videos
    def Set_Url(self, url: str):
        try:
            if url is not None and url != '':
                self.url = url
        except Exception as e:
            #Leite den Fehler eine Ebene Weiter
            raise e

    #Downloade das Video
    def Download_from_Url(self):
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                self.info = ydl.extract_info(self.url)
                self.filename = ydl.prepare_filename(self.info)
                self.title = self.info.get('title', None)
        except Exception as e:
            raise e

    def __del__(self):
        logger.info('Object Download destroyed')