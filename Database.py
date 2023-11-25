import pymongo
from dotenv import load_dotenv
import os
from datetime import datetime
import time
load_dotenv()

DATABASE_SERVER = os.getenv("MONGO_DB_SERVER")
class Database:
    def __init__(self):
       pass