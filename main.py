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
import commands.delete_material as delete_material

from Views.MaterialDropDown import *

from config import *

from plot import plot_function

import requests

# Configurations
TOKEN = os.getenv("TOKEN")
intents = discord.Intents.all()

logging.basicConfig(level=logging.INFO)
discord.utils.setup_logging()

# Graph plotting
PLOTTING_CHANNEL = 1214739737932337212 # CMP
x_min = -30
x_max = 30
num_points = 1000

def send_poll():
    # Channel ID where you want to send the message
    channel_id = "1157439694058049637"

    # Message payload
    payload = {
        "content": "",
        "tts":False,
        "flags":0,
        "poll":{
            "question":{"text":"test"},
            "answers":[
                {"poll_media":{"text":"t1"}},
                {"poll_media":{"text":"t2"}}
            ],
            "allow_multiselect":False,
            "duration":24,
            "layout_type":1
        }
    }

    # Headers with authorization
    headers = {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type": "application/json"
    }

    # Send POST request to Discord API
    url = f"https://discord.com/api/v9/channels/{1157439694058049637}/messages"
    response = requests.post(url, json=payload, headers=headers)

    # Check if the message was sent successfully
    if response.status_code == 200:
        print("Message sent successfully.")
    else:
        print("Failed to send message. Status code:", response.status_code)
        print(response.json())
# Bot
class CUFEBot(commands.Bot):
    def __init__(self, activity=discord.Activity(type=discord.ActivityType.listening, name="you"), status=discord.Status.online):
        super().__init__(intents=intents, command_prefix='!', activity=activity, status=status)  # Prefix

        self.synced = False
        self.database = Database()
        self.semesters = list(self.database.get_all_semesters())
        self.logs_channels = {}

    
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

        for gid, LOGS_CHANNEL in LOGS_CHANNELS.items():
            _channel = self.get_channel(LOGS_CHANNEL)
            if _channel is None:
                try:
                    _channel = await self.fetch_channel(LOGS_CHANNEL)
                except:
                    print("Logs channel not found")
                    continue
            self.logs_channels[gid] = _channel

    async def on_message(self, message):
        if message.author.bot:
            return
        #if message.content.startswith('poll'):
        #    send_poll()
        if message.channel.id == PLOTTING_CHANNEL  and message.content.startswith('p'):
            function_str = message.content[1:]
            function_str = function_str.strip()

            # Attempt to generate the plot image
            plot_data = plot_function(function_str, x_min, x_max, num_points)

            if plot_data is not None:
                # Send the generated image as a file
                await message.channel.send(f"`Plotting function: f(x) = {function_str}`", file=discord.File(plot_data, filename='plot.png'))
            else:
                # Inform the user about the error
                await message.channel.send("`Error generating plot. Please check the function syntax.`")
        

    async def sync_commands(self):
        await set_channel.sync_command(self, guild_ids)
        await unset_channel.sync_command(self, guild_ids)
        await register_semester.sync_command(self, guild_ids)
        await register_course.sync_command(self, guild_ids)
        await push_material.sync_command(self, guild_ids)
        await add_week.sync_command(self, guild_ids)
        await send_embed.sync_command(self, guild_ids)
        await delete_material.sync_command(self, guild_ids)

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
        logs_channel = self.logs_channels[interaction.guild.id]

        if logs_channel is None:
            return
        user = interaction.user
        channel = interaction.channel

        embed = discord.Embed(title=f"Material Logs", description=f"**Material:** {material_name}\n**Week:** {week}\n**Course:** {course}\n**{action.title()} by:** {user.mention}\n**In:** {channel.mention}", color=discord.Color.blurple())
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        await logs_channel.send(embed=embed)

# Run
bot = CUFEBot()

#@bot.event
#async def on_voice_state_update(member: discord.Member, before, after):
#    if member.bot:
#        return
#    voice_client = member.guild.voice_client
#    is_in_voice = voice_client is not None and voice_client.channel is not None
#    if voice_client is not None:
#        channel = voice_client.channel
#        if channel and (len(channel.members) <= 1):
#            await voice_client.disconnect(force=True)
#            print(f"Bot has left {channel.name}")
#            is_in_voice = False
#    if after.channel is not None:
#        # Member joined a voice channel
#        channel: discord.VoiceChannel = after.channel
#        if not is_in_voice:
#            voice_client = await channel.connect()
#        else:
#            if voice_client.channel != channel:
#                await voice_client.move_to(channel)
#        print(f"Bot has joined {channel.name}")
#        pass  # You can add logic here if needed

bot.run(TOKEN)