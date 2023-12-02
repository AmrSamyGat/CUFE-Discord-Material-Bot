import discord
from discord.ext import commands, tasks
from discord import app_commands

import logging
import os

from Database import Database

import commands.set_channel as set_channel
import commands.unset_channel as unset_channel
import commands.register_semester as register_semester
import commands.register_course as register_course
import commands.push_material as push_material
import commands.add_week as add_week
import commands.send_embed as send_embed

from Views.MaterialDropDown import *

from config import *


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
        
        for semester in self.semesters:
            self.add_view(MaterialWeeksView(self, semester))
            weeks = self.database.get_semester_weeks(semester)
            for week in weeks:
                self.add_view(MaterialCoursesView(self, semester, week))
            print(f"Added views for semester {semester}")

        self.logs_channel = self.get_channel(LOGS_CHANNEL)
        if self.logs_channel is None:
            try:
                self.logs_channel = await self.fetch_channel(LOGS_CHANNEL)
            except:
                print("Logs channel not found")

    async def on_message(self, message):
        if message.author.bot:
            return
        

    async def sync_commands(self):
        await set_channel.sync_command(self, guild_ids)
        await unset_channel.sync_command(self, guild_ids)
        await register_semester.sync_command(self, guild_ids)
        await register_course.sync_command(self, guild_ids)
        await push_material.sync_command(self, guild_ids)
        await add_week.sync_command(self, guild_ids)
        await send_embed.sync_command(self, guild_ids)

    async def refresh(self):
        self.semesters = list(self.database.get_all_semesters())

        channels = self.database.get_channels()
        for chid in channels:
            channel = self.get_channel(chid)
            if channel is None:
                try:
                    channel = await self.fetch_channel(chid)
                except:
                    continue
            
            async for msg in channel.history(limit=10):
                msg: discord.Message
                if msg.author.id == self.user.id and msg.components:
                    for component in msg.components:
                        if component.children[0].custom_id and component.children[0].custom_id.startswith("week_select"):
                            has_semester = component.children[0].custom_id.split("-")
                            if len(has_semester) == 2:
                                await msg.edit(view=MaterialWeeksView(self, has_semester[1]))
                                print(f"Updated Week View for #{channel.name} in {channel.guild.name}")

    async def send_logs(self, interaction: discord.Interaction, material_name: str, week: int, course: str, action = "requested"):
        if self.logs_channel is None:
            return
        user = interaction.user
        channel = interaction.channel
        embed = discord.Embed(title=f"Material Logs", description=f"**Material:** {material_name}\n**Week:** {week}\n**Course:** {course}\n**{action.title()} by:** {user.mention}\n**In:** {channel.mention}", color=discord.Color.blurple())
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        await self.logs_channel.send(embed=embed)

# Run
bot = CUFEBot()
bot.run(TOKEN)