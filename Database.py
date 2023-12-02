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
    def get_semester_id(self, guild_id: int, semester: int, year: int):
        return str(semester)+"_"+str(year)+"_"+str(guild_id)
    def convert_semester_id(self, semester_id: str): # returns semester, year, guild_id
        return semester_id.split("_")

    def get_semester(self, guild_id: int, semester: int, year: int):
        return self.semesters.find_one({"_id": self.get_semester_id(guild_id, semester, year), "guild_id":guild_id})
    def get_semester_from_id(self, semester_id: str):
        return self.semesters.find_one({"_id": semester_id})
    def register_semester(self, guild_id: int, semester: int, year: int):
        if self.get_semester(guild_id, semester, year) is None:
            self.semesters.insert_one({"_id": self.get_semester_id(guild_id, semester, year), "guild_id":guild_id, "semester":semester, "year": year, "weeks":[], "courses":{}})
            return True
        return False

    def get_all_semesters(self): # returns all semester IDS
        return [s["_id"] for s in list(self.semesters.find({}))]
    
    def get_semesters(self, guild_id: int):
        return list(self.semesters.find({"guild_id":guild_id}))
    
    def add_week(self, semester_id: str, week: int):
        semester = self.get_semester_from_id(semester_id)
        if week in semester["weeks"]:
            return False
        semester["weeks"].append(week)
        self.semesters.update_one({"_id": semester_id}, {"$set": semester})
        return True
    
    def get_weeks(self, guild_id: int, with_semester: bool=False):
        semesters = self.get_semesters(guild_id)
        weeks = []
        for semester in semesters:
            if with_semester:
                for week in semester["weeks"]:
                    s = self.convert_semester_id(semester["_id"])
                    weeks.append((week, s[0], s[1]))
            else:
                weeks += semester["weeks"]
        return weeks

    def get_semester_weeks(self, semester_id: str):
        return self.get_semester_from_id(semester_id)["weeks"]
    
    def register_course(self, semester_id: str, course_id: str):
        semester = self.get_semester_from_id(semester_id)
        semester["courses"][course_id] = {"name": course_id, "materials": []}
        self.semesters.update_one({"_id": semester_id}, {"$set": semester})
    
    def get_courses(self, guild_id: int, with_semester: bool=False):
        semesters = self.get_semesters(guild_id)
        courses = []
        for semester in semesters:
            if with_semester:
                for course in semester["courses"]:
                    s = self.convert_semester_id(semester["_id"])
                    courses.append((course, s[0], s[1]))
            else:
                courses += list(semester["courses"].keys())
        return courses
        
    def get_semester_courses(self, semester_id: str):
        return self.get_semester_from_id(semester_id)["courses"]
    
    def get_semester_course(self, semester_id: str, course_id: str):
        return self.get_semester_courses(semester_id)[course_id]
    
    def get_semester_course_materials(self, semester_id: str, course_id: str):
        return self.get_semester_course(semester_id, course_id)["materials"]
    
    def get_semester_course_materials_byweek(self, semester_id: str, course_id: str, week: int):
        materials = self.get_semester_course_materials(semester_id, course_id)
        return [material for material in materials if material["week"] == week]

    def push_material(self, semester_id: str, course_id: str, title: str, description: str, week: int, links: list=[], date: datetime=datetime.now()):
        materials = self.get_semester_course_materials(semester_id, course_id)

        material = {
            "id": len(materials), 
            "title": title, 
            "description": description, 
            "week": week, 
            "links": links, 
            "date": date
        }

        materials.append(material)

        self.semesters.update_one({"_id": semester_id}, {"$set": {"courses."+course_id+".materials": materials}})

    def get_semester_course_material(self, semester_id: str, course_id: str, material_id: int):
        materials = self.get_semester_course_materials(semester_id, course_id)
        for material in materials:
            if material["id"] == material_id:
                return material
    
    

