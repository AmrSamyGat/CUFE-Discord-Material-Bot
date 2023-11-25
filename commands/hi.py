import discord
from discord.ext import commands
from discord import app_commands

#from Database import Database

from config import *

async def sync_command(bot:commands.Bot, guild_ids:[]):
    @bot.tree.command(name ="hi", description="Hi", guilds=[discord.Object(id=gid) for gid in guild_ids]) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
    async def hi(interaction: discord.Interaction, text:str = "Hi"):
        await interaction.response.defer(ephemeral=False, thinking=True)

        #e = discord.Embed(color=discord.Color.blue(), title="BeachCombing", description=f"**You can use the bot in <#{channel.id}> now ✅**", timestamp = discord.utils.utcnow())
        #e.set_footer(text="BeachCombing Bot")
        await interaction.followup.send(content=text)