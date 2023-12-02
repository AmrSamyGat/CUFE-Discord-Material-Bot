import discord
from discord.ext import commands
from discord import app_commands

from Database import Database

from config import *
from Views.MaterialDropDown import MaterialWeeksView

async def sync_command(bot:commands.Bot, guild_ids:[]):
    @bot.tree.command(name ="send_embed", description="Sends the embed of material into a channel.", guilds=[discord.Object(id=gid) for gid in guild_ids]) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
    @discord.app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def send_embed(interaction: discord.Interaction, semester: str, channel: discord.TextChannel):
        if interaction.channel.id not in bot.database.get_channels():
            return
        await interaction.response.defer(ephemeral=False, thinking=True)
        
        embed = discord.Embed(title="CMP 27", description=f"**Welcome to our materials channel.**\nChoose a week to show its material :)", color=discord.Color.blue())
        embed.set_footer(text="CUFE CMP 27")
        embed.set_thumbnail(url=interaction.guild.icon.url)

        weeksView = MaterialWeeksView(bot, semester)
        await channel.send(embed=embed, view=weeksView)

    @send_embed.autocomplete('semester')
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