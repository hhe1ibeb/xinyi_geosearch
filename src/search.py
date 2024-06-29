from src.embedding import get_embedding
import pymongo
import os
from dotenv import load_dotenv
from langdetect import detect

load_dotenv()
CONNECTION_STRING = os.getenv("MONGODB_URI")

mongo_client = pymongo.MongoClient(CONNECTION_STRING)
db = mongo_client["xinyi_geodata"]
collection = db["collection_1"]

def detect_language(text):
    return detect(text)

def vector_search(user_query, collection, lang):
    """
    Perform a vector search in the MongoDB collection based on the user query.

    Args:
    user_query (str): The user's query string.
    collection (MongoCollection): The MongoDB collection to search.

    Returns:
    list: A list of matching documents.
    """

    # Generate embedding for the user query
    query_embedding = get_embedding(user_query, lang=lang)

    if query_embedding is None:
        return "Invalid query or embedding generation failed."
    
    path = ""
    index = ""
    if lang == "zh":
        path = "embedding-zh"
        index = "vector_index_zh"
    else: 
        path = "embedding-en"
        index = "vector_index"

    # Define the vector search pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": index,
                "queryVector": query_embedding,
                "path": path,
                "numCandidates": 150,  # Number of candidate matches to consider
                "limit": 10,  # Return top 4 matches
            }
        },
        {
            "$project": {
                "_id": 0,
                "lat": 1,
                "lon": 1,
                "description": 1,
                "fwd": 1,
                "l": 1,
                "r": 1,
                "descriptions-mandarin": 1,
                "score": {"$meta": "vectorSearchScore"},  # Include the search score
            }
        },
    ]

    # Execute the search
    results = collection.aggregate(pipeline)
    return list(results)

def get_search_result(query, collection, lang):

    get_knowledge = vector_search(query, collection, lang)

    search_result = ""
    des = ""
    if lang != "zh": des = "description"
    else: des = "descriptions-mandarin"
    for result in get_knowledge:
        search_result += f"Lat: {result.get('lat', 'N/A')}, Lon: {result.get('lon', 'N/A')}, Description: {result.get(des, 'N/A')}\n"

    return search_result