import discord
from .Arrows import ArrowButton
from .SearchButton import SearchButton
from Map import Map

class CUFEView(discord.ui.View):
    def __init__(self):
        super().__init__()
