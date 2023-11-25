import discord
from discord.ext import commands, tasks
from discord import app_commands

import logging
import os

#from Database import Database
import commands.set_channel as set_channel
#import commands.unset_channel as unset_channel


from config import guild_ids


# Configurations
TOKEN = os.getenv("TOKEN")
intents = discord.Intents.all()

logging.basicConfig(level=logging.INFO)
discord.utils.setup_logging()

# Bot
class CUFEBot(commands.Bot):
    def __init__(self):
        super().__init__(intents=intents, command_prefix='!')  # Prefix

        self.synced = False
        #self.database = Database()

    
    async def on_ready(self):
        await self.wait_until_ready()
        print(f'Logged in as {self.user.name}')
        await self.sync_commands()
        if not self.synced:
            print("Syncing commands")
            for gid in guild_ids:
                await self.tree.sync(guild=discord.Object(id = gid))
            self.synced = True
            print("Commands synced")

    async def on_message(self, message):
        if message.author.bot:
            return
        

    async def sync_commands(self):
        await set_channel.sync_command(self, guild_ids)
        #await unset_channel.sync_command(self, guild_ids)


# Run
bot = CUFEBot()
bot.run(TOKEN)