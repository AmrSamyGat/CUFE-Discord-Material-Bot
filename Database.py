import pymongo
from dotenv import load_dotenv
import os
from datetime import datetime
import time
load_dotenv()
"""
Database structure:
- users
    - _id: int
    - join_time: datetime
- guilds
    - _id: int
- channels
    - _id: int
- semesters
    - _id: semester_year
    - guild_id: int
    - semester: int
    - year: int
    - weeks: list of weeks
        - id: int
    - courses: list of courses
        - course_id
        - course_name
        - materials: list of materials
            - id: int
            - week: int
            - title: str
            - links: list of links
                - link: str
                - title: str
            - description: str
            - date: datetime
"""
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
    def get_semester_id(self, semester: int, year: int):
        return str(semester)+"_"+str(year)
    def register_semester(self, guild_id: int, semester: int, year: int):
        self.semesters.insert_one({"_id": self.get_semester_id(semester, year), "guild_id":guild_id, "semester":semester, "year": year, "weeks":[], "courses":{}})

    def get_semester(self, semester: int, year: int):
        return self.semesters.find_one({"_id": self.get_semester_id(semester, year)})
    
    def get_semesters(self):
        return list(self.semesters.find({}))
    
    def add_week(self, semester: int, year: int, week: int):
        semester = self.get_semester(semester, year)
        semester["weeks"].append(week)
        self.semesters.update_one({"_id": self.get_semester_id(semester, year)}, {"$set": semester})
    def get_semester_weeks(self, semester: int, year: int):
        return self.get_semester(semester, year)["weeks"]
    
    def register_course(self, semester: int, year: int, course_id: str, course_name: str):
        semester = self.get_semester(semester, year)
        semester["courses"][course_id] = {"name": course_name, "materials": []}
        self.semesters.update_one({"_id": self.get_semester_id(semester, year)}, {"$set": semester})
    
    def get_semester_courses(self, semester: int, year: int):
        return self.get_semester(semester, year)["courses"]
    
    def get_semester_course(self, semester: int, year: int, course_id: str):
        return self.get_semester_courses(semester, year)[course_id]
    
    def get_semester_course_materials(self, semester: int, year: int, course_id: str):
        return self.get_semester_course(semester, year, course_id)["materials"]

    def push_material(self, semester: int, year: int, course_id: str, title: str, description: str, week: int, links: list=[], date: datetime=datetime.now()):
        materials = self.get_semester_course_materials(semester, year, course_id)

        material = {
            "id": len(materials), 
            "title": title, 
            "description": description, 
            "week": week, 
            "links": links, 
            "date": date
        }

        materials.append(material)

        self.semesters.update_one({"_id": self.get_semester_id(semester, year)}, {"$set": {"courses."+course_id+".materials": materials}})

    def get_semester_course_material(self, semester: int, year: int, course_id: str, material_id: int):
        materials = self.get_semester_course_materials(semester, year, course_id)
        for material in materials:
            if material["id"] == material_id:
                return material
    
    

