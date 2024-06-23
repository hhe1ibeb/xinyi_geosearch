from pymongo import MongoClient
import os
from dotenv import load_dotenv
from langdetect import detect

load_dotenv()
CONNECTION_STRING = os.getenv("MONGODB_URI")

mongo_client = MongoClient(CONNECTION_STRING)
db = mongo_client["geosearch_evaluation"]
user_choices_collection = db["evaluation"]

