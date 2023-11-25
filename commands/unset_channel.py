import discord
from discord.ext import commands
from discord import app_commands

from Database import Database
from Map import Map

from config import *

async def sync_command(bot:commands.Bot, guild_ids:[]):
    @bot.tree.command(name ="unset_channel", description="Restrict the bot to be used in specific channels.", guilds=[discord.Object(id=gid) for gid in guild_ids]) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
    @discord.app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def unset_channel(interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=False, thinking=True)
        db: Database = bot.database
        
        is_unset = db.unset_channel(channel.id)
        if not is_unset:
            await interaction.followup.send("`This channel isn't registered.`")
            return
        bot.refresh_maps()

        e = discord.Embed(color=discord.Color.blue(), title="BeachCombing", description=f"**You cannot use the bot in <#{channel.id}> now ✅**", timestamp = discord.utils.utcnow())
        e.set_footer(text="BeachCombing Bot")
        await interaction.followup.send(embed=e)