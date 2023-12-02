import discord
from discord.ext import commands
from discord import app_commands

from Database import Database

from config import *

async def sync_command(bot:commands.Bot, guild_ids:[]):
    @bot.tree.command(name ="register_semester", description="Register a new semester into the bot.", guilds=[discord.Object(id=gid) for gid in guild_ids]) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
    @discord.app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def register_semester(interaction: discord.Interaction, semester: int, year: int):
        if interaction.channel.id not in bot.database.get_channels():
            return
        await interaction.response.defer(ephemeral=False, thinking=True)
        db: Database = bot.database
        
        is_semester_registered = db.register_semester(interaction.guild.id, semester, year)
        if not is_semester_registered:
            await interaction.followup.send("`This semester is already registered.`")
            return
        
        await bot.refresh() # refreshes semesters list

        await interaction.followup.send("`This semester is registered successfully.`")