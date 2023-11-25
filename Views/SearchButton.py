import discord
from Map import Map
from Database import Database
from random import choice
from items_config import *
from config import *
import os
from discord import Webhook
from aiohttp import ClientSession
import time

class SearchButton(discord.ui.Button):
    def __init__(self, PlayView, user_id, cMap: Map, bot, row=None, user_position=tuple[int, int], disabled=False):
        super().__init__(style=discord.ButtonStyle.primary, label="Dig", custom_id=f"search_btn_{user_id}", emoji="🔍",row=row, disabled=disabled)
        self.cMap = cMap
        self.user_id = user_id
        self.user_position = user_position
        self.bot = bot
        self.db: Database = bot.database
        self.PlayView = PlayView

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        if interaction.user.id != self.user_id:
            return
        view = self.view


async def sendWebhook(webhookURL, msgText, userName, avatarURL=None, embeds=[], files=[]): # We use this to send through discord webhooks
    async with ClientSession() as session:
        webhook = Webhook.from_url(webhookURL, session=session)
        await webhook.send(content=msgText, username=userName, avatar_url=avatarURL, embeds=embeds, files=files)