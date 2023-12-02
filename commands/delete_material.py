import discord
from discord.ext import commands
from discord import app_commands

from Database import Database
from Views.DeleteMaterialButton import DeleteMaterialView

from config import *

async def sync_command(bot:commands.Bot, guild_ids:[]):
    @bot.tree.command(name ="delete_material", description="Deletes material from the bot.", guilds=[discord.Object(id=gid) for gid in guild_ids]) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
    @discord.app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def delete_material(interaction: discord.Interaction, semester: str, course: str, week: int):
        if interaction.channel.id not in bot.database.get_channels():
            return
        await interaction.response.defer(ephemeral=True, thinking=True)
        db: Database = bot.database
        
        materials = db.get_semester_course_materials_byweek(semester, course, week)
        if len(materials) == 0:
            await interaction.followup.send(f"`There is no material for this week to delete.`")
            return
        
        materials_text = ""
        for material in materials:
            materials_text += f"• {material['title']} (ID: {material['id']})\n"
        
        embed = discord.Embed(title=f"Material for Week {week} - {course}", description=f"**Available Materials:**\n{materials_text}\n\n**Click on any of the available buttons to delete its corresponding material**", color=discord.Color.blurple())

        delete_material_view = DeleteMaterialView(bot, semester, course, materials, week)
        await interaction.followup.send(embed=embed, view=delete_material_view)

    @delete_material.autocomplete('semester')
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
    
    @delete_material.autocomplete('course')
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
    
    @delete_material.autocomplete('week')
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