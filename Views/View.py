import discord
from .Arrows import ArrowButton
from .SearchButton import SearchButton
from Map import Map

class PlayView(discord.ui.View):

    arrows: list[ArrowButton]
    searchButton: SearchButton

    def __init__(self, user_id, cMap: Map, bot, user_position: tuple[int, int], all_arrows_disabled=False, search_disabled=False):
        super().__init__()

        for direction in ["up", "down"]:
            next_point = (user_position[0], user_position[1]+(-1 if direction == "up" else 1))
            self.add_item(ArrowButton(PlayView, direction, user_id, cMap, bot, row=0, user_position=user_position, disabled=all_arrows_disabled or ((not cMap.isPlayArea(next_point)) or cMap.isWall(next_point))))
        self.add_item(SearchButton(PlayView, user_id, cMap, bot, row=0, user_position=user_position, disabled=search_disabled or cMap.isSpawnPoint(user_position[0], user_position[1])))
        for direction in ["left", "right"]:
            next_point = (user_position[0]+(1 if direction == "right" else -1), user_position[1])
            self.add_item(ArrowButton(PlayView, direction, user_id, cMap, bot, row=1, user_position=user_position, disabled=all_arrows_disabled or ((not cMap.isPlayArea(next_point)) or cMap.isWall(next_point))))