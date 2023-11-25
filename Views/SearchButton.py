import discord
from Map import Map
from Database import Database
from random import choice
from items_config import *
from config import *
import os
from discord import Webhook
from aiohttp import ClientSession
import time

class SearchButton(discord.ui.Button):
    def __init__(self, PlayView, user_id, cMap: Map, bot, row=None, user_position=tuple[int, int], disabled=False):
        super().__init__(style=discord.ButtonStyle.primary, label="Dig", custom_id=f"search_btn_{user_id}", emoji="🔍",row=row, disabled=disabled)
        self.cMap = cMap
        self.user_id = user_id
        self.user_position = user_position
        self.bot = bot
        self.db: Database = bot.database
        self.PlayView = PlayView

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        if interaction.user.id != self.user_id:
            return
        view = self.view

        await interaction.response.defer(ephemeral=True, thinking=True)

        searches_count = self.db.get_user_searches_count(self.user_id, self.cMap.id)
        last_search_time = self.db.get_user_last_search_time(self.user_id, self.cMap.id)
        
        if last_search_time == 0:
            self.db.set_user_last_search_time(self.user_id, self.cMap.id)
            last_search_time = self.db.get_user_last_search_time(self.user_id, self.cMap.id)
        
        c_time = time.time()
        hours_since_last_search = (c_time - last_search_time) / 3600
        print(interaction.user.name, "Searching", c_time, last_search_time, hours_since_last_search, searches_count)
        if searches_count >= SEARCHES_PER_DAY:
            print("triggered more than search per day")
            if hours_since_last_search < 24:
                await interaction.followup.send(f"`You have already searched {SEARCHES_PER_DAY}/{SEARCHES_PER_DAY} times today! You can search again in {round(24 - hours_since_last_search, 2)} hours.`", ephemeral=True)
                return
            else:
                print("triggered")
                self.db.set_user_searches_count(self.user_id, self.cMap.id, 0)
                self.db.set_user_last_search_time(self.user_id, self.cMap.id)
                searches_count = 0

        items_manager = ItemsManager(self.cMap)

        items = list(self.db.get_map_items_at_position(self.cMap.id, self.user_position))
        items_temp = list(items)
        creation_time = self.db.get_map_creation_date(self.cMap.id)

        for item in items:
            i_dict = items_manager.get_item_from_id(item)
            is_daily = ('spawn_by_day' in i_dict and i_dict['spawn_by_day'] == True)
            if is_daily:
                days_passed_after_creation = (c_time - creation_time) / 86400
                if (days_passed_after_creation < (i_dict['day']-TRACKS_UNLOCKED_PER_DAY+1)) and item in items_temp:
                    items_temp.remove(item)

        item_id = choice(items_temp) if len(items_temp) > 0 else EMPTY_ITEM
        item_dict = items_manager.get_item_from_id(item_id)
        c_time = time.time()
                    
        if item_id != EMPTY_ITEM and item_id in items:
            items.remove(item_id)
            self.db.set_map_items_at_position(self.cMap.id, self.user_position, items)
        self.bot.refresh_maps()

        item = items_manager.get_item_from_id(item_id)

        if item_id != EMPTY_ITEM:
            self.db.add_user_map_item(self.user_id, self.cMap.id, item_id, 1)
            self.db.set_user_map_last_item_picked_up(self.user_id, self.cMap.id, item_id)

        self.db.set_user_searches_count(self.user_id, self.cMap.id, searches_count+1)
        searches_left = SEARCHES_PER_DAY-searches_count-1 if SEARCHES_PER_DAY-searches_count-1 >= 0 else 0
        
        _embed = discord.Embed(color=item["color"], title=f"{item['emoji']} {item['name']}", description=f"**You earned: {item['name']}**\n{item['description']}\n**Reward ({item['reward']['type']}): {item['reward']['amount']}**\n\n**You have {searches_left}/{SEARCHES_PER_DAY} Searches left for today.**", timestamp = discord.utils.utcnow())
        attachment = None
        if item['type'] != "track list" and item['type'] != "empty":
            attachment = discord.File(os.path.join('./assets', item_id+".png"), filename="item.png")
            _embed.set_thumbnail(url="attachment://item.png")
        await interaction.followup.send(embed=_embed, file=attachment or discord.utils.MISSING, ephemeral=True)

        if searches_left == 0:
            embed = interaction.message.embeds[0]
            embed.description = "You have no more searches left for today!"
            #await interaction.message.edit
            await interaction.followup.send(embed=embed, files=[], view=self.PlayView(self.user_id, self.cMap, self.bot, self.user_position, all_arrows_disabled=True, search_disabled=True), ephemeral=True)
        else:
            embed = interaction.message.embeds[0]
            moves_left = MOVES_PER_DAY-self.db.get_user_moves_count(self.user_id, self.cMap.id)
            moves_left = moves_left if moves_left >= 0 else 0
            embed.description = f"You have **{moves_left}/{MOVES_PER_DAY} moves**\nand **{searches_left}/{SEARCHES_PER_DAY} searches** left for today.\nUse the available arrows to move!"
            #await interaction.message.edit
            await interaction.followup.send(embed=embed, files=[], view=view, ephemeral=True)
        
        user_items = dict(self.db.get_user_map_items(interaction.user.id, self.cMap.id))
        points_worth = 0
        for item_id, amount in user_items.items():
            item_info = items_manager.get_item_from_id(item_id)
            item_info = item_info if item_info['name'] != "Nothing" else {'name':item_id, 'emoji':'❓'}
            points_worth += item_info['reward']['amount']*amount if item_info['reward']['type'] == "points" else 0

        if interaction.guild.id in ROLES_AFTER_AMOUNT:
            for amount, role_id in ROLES_AFTER_AMOUNT[interaction.guild.id].items():
                if points_worth >= amount:
                    role = interaction.guild.get_role(role_id)
                    if role not in interaction.user.roles:
                        await interaction.user.add_roles(role)
                        _embed2 = discord.Embed(color=discord.Color.green(), title=f"🎉 Congratulations, you earned the {role.name} role! 🎉", description=f"**{interaction.user.name}** has earned the **{role.name}** role by collecting more than **{points_worth}** points!", timestamp = discord.utils.utcnow())
                        _embed2.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar and interaction.user.avatar.url else interaction.user.default_avatar.url)
                        await interaction.followup.send(embed=_embed2)



        if item['type'] in ITEMS_TO_SHOUTOUT and interaction.guild.id in RARE_ITEMS_WEBHOOKS:
            for webhook in RARE_ITEMS_WEBHOOKS[interaction.guild.id]:
                _embed2 = discord.Embed(color=item["color"], title=f"{item['emoji']} {item['name']}", description=f"**{interaction.user.name}** found a **{item['name']}**!", timestamp = discord.utils.utcnow())
                _embed2.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar and interaction.user.avatar.url else interaction.user.default_avatar.url)
                await sendWebhook(webhook, "", WEBHOOK_NAME, embeds=[_embed2])



async def sendWebhook(webhookURL, msgText, userName, avatarURL=None, embeds=[], files=[]): # We use this to send through discord webhooks
    async with ClientSession() as session:
        webhook = Webhook.from_url(webhookURL, session=session)
        await webhook.send(content=msgText, username=userName, avatar_url=avatarURL, embeds=embeds, files=files)