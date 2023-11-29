import discord
from discord.ext import commands
from discord import app_commands

from Database import Database
from Views.PushMaterialModal import PushMaterialModal

from config import *

async def sync_command(bot:commands.Bot, guild_ids:[]):
    @bot.tree.command(name ="push_material", description="Pushes new semester material into the bot.", guilds=[discord.Object(id=gid) for gid in guild_ids]) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
    @discord.app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def push_material(interaction: discord.Interaction, semester: str, course: str, week: int):
        if interaction.channel.id not in bot.database.get_channels():
            return
        db: Database = bot.database
        
        await interaction.response.send_modal(PushMaterialModal(bot, semester, course, week))

    @push_material.autocomplete('semester')
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
    
    @push_material.autocomplete('course')
    async def autocompletec(
        interaction: discord.Interaction,
        current: str,
    ):
        semesters = bot.semesters
        db: Database = bot.database
        courses = db.get_courses(interaction.guild.id, True)
        return [
            app_commands.Choice(name=f"{course[0]} (Semester {course[1]} Year {course[2]})", value=course[0])
            for course in courses
        ]
    
    @push_material.autocomplete('week')
    async def autocompletew(
        interaction: discord.Interaction,
        current: str,
    ):
        semesters = bot.semesters
        db: Database = bot.database
        weeks = db.get_weeks(interaction.guild.id, True)
        return [
            app_commands.Choice(name=f"Week {week[0]} (Semester {week[1]} Year {week[2]})", value=week[0])
            for week in weeks
        ]