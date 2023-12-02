import discord
from discord.ext import commands
from discord import app_commands

from Database import Database

from config import *

async def sync_command(bot:commands.Bot, guild_ids:[]):
    @bot.tree.command(name ="register_course", description="Registers a new course into the bot.", guilds=[discord.Object(id=gid) for gid in guild_ids]) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
    @discord.app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def register_course(interaction: discord.Interaction, semester: str, course: str):
        if interaction.channel.id not in bot.database.get_channels():
            return
        await interaction.response.defer(ephemeral=False, thinking=True)
        db: Database = bot.database
        
        db.register_course(semester, course)

        await interaction.followup.send(f"`{course.title()} course is registered successfully.`")

    @register_course.autocomplete('semester')
    async def autocomplete(
        interaction: discord.Interaction,
        current: str,
    ):
        semesters = bot.semesters
        db: Database = bot.database
        return [
            app_commands.Choice(name=f"Semester {db.convert_semester_id(semester)[0]} Year {db.convert_semester_id(semester)[1]} ({interaction.guild.name})", value=semester)
            for semester in semesters if str(interaction.guild.id) in semester
        ]