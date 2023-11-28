import pymongo
from dotenv import load_dotenv
import os
from datetime import datetime
import time
load_dotenv()

DATABASE_SERVER = os.getenv("MONGO_DB_SERVER")
DATABASE_NAME = os.getenv("MONGO_DB_NAME")

class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(DATABASE_SERVER, maxPoolSize=300)
        self.db = self.client[DATABASE_NAME]
        dblist = self.client.list_database_names()
        if DATABASE_NAME not in dblist:
            print("The database is empty.")
        
        self.users = self.db["users"]
        self.guilds = self.db["guilds"]
        self.channels = self.db["channels"]
        self.semesters = self.db["semesters"]

    def get_users(self):
        return list(self.users.find({}))
    
    def get_guilds(self):
        return list(self.guilds.find({}))

    def get_channels(self):
        return [t['_id'] for t in list(self.channels.find({}))]
    
    def get_user(self, user_id):
        return self.users.find_one({"_id": user_id})
    
    def get_guild(self, guild_id):
        return self.guilds.find_one({"_id": guild_id})
    
    
    def get_channel(self, channel_id):
        return self.channels.find_one({"_id": channel_id})

    def register_user(self, user_id):
        if self.get_user(user_id) is None:
            self.users.insert_one({"_id": user_id, "join_time":datetime.now()})
    
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

    # Material
    def register_semester(self, semester: int, year: int):
        self.semesters.insert_one({"_id": str(semester)+"_"+(year), "semester":semester, "year": year, "courses":{}})

    def get_semester_id(self, semester: int, year: int):
        pass
    

