import pymongo
from dotenv import load_dotenv
import os
from datetime import datetime
import time
load_dotenv()

DATABASE_SERVER = os.getenv("MONGO_DB_SERVER")
class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(DATABASE_SERVER)
        self.db = self.client["beachcombing"]
        dblist = self.client.list_database_names()
        if "beachcombing" not in dblist:
            print("The database is empty.")
        
        self.users = self.db["users"]
        self.guilds = self.db["guilds"]
        self.maps = self.db["maps"]
        self.channels = self.db["channels"]

    def get_users(self):
        return list(self.users.find({}))
    
    def get_guilds(self):
        return list(self.guilds.find({}))

    def get_maps(self):
        return list(self.maps.find({}))

    def get_channels(self):
        return [t['_id'] for t in list(self.channels.find({}))]
    
    def get_user(self, user_id):
        return self.users.find_one({"_id": user_id})
    
    def get_guild(self, guild_id):
        return self.guilds.find_one({"_id": guild_id})
    
    def get_map(self, map_id):
        return self.maps.find_one({"_id": map_id})
    
    def get_channel(self, channel_id):
        return self.channels.find_one({"_id": channel_id})

    def register_user(self, user_id):
        if self.get_user(user_id) is None:
            self.users.insert_one({"_id": user_id, "maps": {}})
    
    def get_user_map(self, user_id, map_id):
        if self.get_user(user_id) is None:
            return None
        return self.get_user(user_id)["maps"].get(map_id)
    def register_user_map(self, user_id, map_id, position):
        if self.get_user(user_id) is None:
            self.register_user(user_id)
        if self.get_user(user_id)["maps"].get(map_id) is None:
            self.users.update_one({"_id": user_id}, {"$set": {"maps."+map_id: {"items":{}, "position":position, "last_move_time":time.time(), "last_search_time":0, "last_item_picked_up":None, "spawn_time":time.time()}}})

    def get_user_map_items(self, user_id, map_id):
        return self.get_user_map(user_id, map_id)["items"]
    def get_user_map_position(self, user_id, map_id):
        return self.get_user_map(user_id, map_id)["position"]
    def get_user_map_last_move(self, user_id, map_id):
        return self.get_user_map(user_id, map_id)["last_move"]
    def get_user_map_last_item_pickup(self, user_id, map_id):
        return self.get_user_map(user_id, map_id)["last_item_pickup"]
    def get_user_map_last_item_picked_up(self, user_id, map_id):
        return self.get_user_map(user_id, map_id)["last_item_picked_up"]
    def get_user_map_item_amount(self, user_id, map_id, item_id):
        return self.get_user_map_items(user_id, map_id).get(item_id) or 0

    def add_user_map_item(self, user_id, map_id, item_id, amount):
        self.users.update_one({"_id": user_id}, {"$set": {"maps."+map_id+".items."+item_id: amount+self.get_user_map_item_amount(user_id, map_id, item_id)}})
    def set_user_map_position(self, user_id, map_id, position):
        self.users.update_one({"_id": user_id}, {"$set": {"maps."+map_id+".position": position}})
    def set_user_map_last_item_picked_up(self, user_id, map_id, last_item_picked_up):
        self.users.update_one({"_id": user_id}, {"$set": {"maps."+map_id+".last_item_picked_up": last_item_picked_up}})
    
    def set_user_moves_count(self, user_id, map_id, moves_count):
        self.users.update_one({"_id": user_id}, {"$set": {"maps."+map_id+".moves_count": moves_count}})
    def get_user_moves_count(self, user_id, map_id):
        return self.get_user_map(user_id, map_id).get("moves_count") or 0
    def set_user_searches_count(self, user_id, map_id, searches_count):
        self.users.update_one({"_id": user_id}, {"$set": {"maps."+map_id+".searches_count": searches_count}})
    def get_user_searches_count(self, user_id, map_id):
        return self.get_user_map(user_id, map_id).get("searches_count") or 0

    def set_user_last_move_time(self, user_id, map_id, last_move_time=time.time()):
        self.users.update_one({"_id": user_id}, {"$set": {"maps."+map_id+".last_move_time": last_move_time}})
    def set_user_last_search_time(self, user_id, map_id, last_search_time=time.time()):
        self.users.update_one({"_id": user_id}, {"$set": {"maps."+map_id+".last_search_time": last_search_time}})
    def get_user_last_move_time(self, user_id, map_id):
        return self.get_user_map(user_id, map_id).get("last_move_time") or 0
    def get_user_last_search_time(self, user_id, map_id):
        return self.get_user_map(user_id, map_id).get("last_search_time") or 0

    def get_map_items_at_position(self, map_id, position):
        return self.get_map(map_id)["items_matrix"][position[1]][position[0]]

    def set_map_items_at_position(self, map_id, position, items:list):
        self.maps.update_one({"_id": map_id}, {"$set": {"items_matrix."+str(position[1])+"."+str(position[0]): items}})
    
    def register_guild(self, guild_id):
        if self.get_guild(guild_id) is None:
            self.guilds.insert_one({"_id": guild_id})
    
    def register_channel(self, channel_id):
        if self.get_channel(channel_id) is None:
            self.channels.insert_one({"_id": channel_id})
            return True
        return False
    def unset_channel(self, channel_id):
        if self.get_channel(channel_id) is None:
            return False
        self.channels.delete_one({"_id": channel_id})
        return True
    
    def register_map(self, map_id, guild_id, map_name, map_matrix, spawn_points, seed, theme=1):
        if self.get_map(map_id) is None:
            self.maps.insert_one({"_id": map_id, "id": map_id, "creation_date":time.time(),"guild_id":guild_id, "name": map_name, "matrix": map_matrix, "spawn_points": spawn_points, "seed":seed, "items_matrix": [], "active":False, "theme":theme})

    def get_map_creation_date(self, map_id):
        return self.get_map(map_id).get("creation_date") or time.time()
    
    def get_active_map(self, guild_id):
        return self.maps.find_one({"active":True, "guild_id":guild_id})
    def deactivate_maps(self, guild_id):
        self.maps.update_many({"guild_id":guild_id}, {"$set": {"active":False}})
    def set_active_map(self, guild_id, map_id):
        self.maps.update_one({"active":True, "guild_id":guild_id}, {"$set": {"active":False}})
        self.maps.update_one({"_id":map_id}, {"$set": {"active":True}})

    def set_map_items(self, map_id, items_matrix):
        self.maps.update_one({"_id":map_id}, {"$set": {"items_matrix": items_matrix}})
    def get_map_matrix_items(self, map_id):
        return self.get_map(map_id).get("items_matrix") or []
        
    def set_map_theme(self, map_id, theme):
        self.maps.update_one({"_id":map_id}, {"$set": {"theme": theme}})
    def get_map_theme(self, map_id):
        return self.get_map(map_id).get("theme")