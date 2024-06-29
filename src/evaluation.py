from pymongo import MongoClient
import os
from dotenv import load_dotenv
from langdetect import detect

load_dotenv()
CONNECTION_STRING = os.getenv("MONGODB_URI")

mongo_client = MongoClient(CONNECTION_STRING)
db = mongo_client["geosearch_evaluation"]
user_choices_collection = db["evaluation"]

def get_ranking(results, target_lat, target_lon):
    # Create a list of tuples (index, lat, lon)
    locations = []
    for i, result in enumerate(results):
        lat = result.get('lat')
        lon = result.get('lon')
        if lat is not None and lon is not None:
            locations.append((i, lat, lon))

    # Ensure target_lat and target_lon are not None
    if target_lat is None or target_lon is None:
        return None

    # Sort the list based on proximity to the target coordinates
    locations.sort(key=lambda x: (x[1] - target_lat) ** 2 + (x[2] - target_lon) ** 2)

    # Find the rank of the target coordinates
    for rank, (index, lat, lon) in enumerate(locations):
        if lat == target_lat and lon == target_lon:
            return rank + 1  # Return rank as 1-based index

    return None
