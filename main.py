import discord
from discord.ext import commands, tasks
from discord import app_commands

import logging
import os

from Database import Database

import commands.hi as hi
import commands.set_channel as set_channel
import commands.unset_channel as unset_channel
import commands.register_semester as register_semester
import commands.register_course as register_course
import commands.push_material as push_material
import commands.add_week as add_week



from config import guild_ids


# Configurations
TOKEN = os.getenv("TOKEN")
intents = discord.Intents.all()

logging.basicConfig(level=logging.INFO)
discord.utils.setup_logging()

# Bot
class CUFEBot(commands.Bot):
    def __init__(self, activity=discord.Activity(type=discord.ActivityType.listening, name="Your Suffering"), status=discord.Status.dnd):
        super().__init__(intents=intents, command_prefix='!', activity=activity, status=status)  # Prefix

        self.synced = False
        self.database = Database()
        self.semesters = list(self.database.get_all_semesters())

    
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
        await hi.sync_command(self, guild_ids)
        await set_channel.sync_command(self, guild_ids)
        await unset_channel.sync_command(self, guild_ids)
        await register_semester.sync_command(self, guild_ids)
        await register_course.sync_command(self, guild_ids)
        await push_material.sync_command(self, guild_ids)
        await add_week.sync_command(self, guild_ids)

    def refresh(self):
        self.semesters = list(self.database.get_all_semesters())

# Run
bot = CUFEBot()
bot.run(TOKEN)