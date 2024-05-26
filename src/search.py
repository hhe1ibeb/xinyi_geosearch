from src.embedding import get_embedding
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()
CONNECTION_STRING = os.getenv("MONGODB_URI")

mongo_client = pymongo.MongoClient(CONNECTION_STRING)
db = mongo_client["xinyi_geodata"]
collection = db["collection_1"]

def vector_search(user_query, collection):
    """
    Perform a vector search in the MongoDB collection based on the user query.

    Args:
    user_query (str): The user's query string.
    collection (MongoCollection): The MongoDB collection to search.

    Returns:
    list: A list of matching documents.
    """

    # Generate embedding for the user query
    query_embedding = get_embedding(user_query)

    if query_embedding is None:
        return "Invalid query or embedding generation failed."

    # Define the vector search pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 150,  # Number of candidate matches to consider
                "limit": 10,  # Return top 4 matches
            }
        },
        {
            "$project": {
                "_id": 0,  # Exclude the _id field
                "lat": 1,  # Include the lat field
                "lon": 1,  # Include the lon field
                "description": 1,  # Include the description field
                "score": {"$meta": "vectorSearchScore"},  # Include the search score
            }
        },
    ]

    # Execute the search
    results = collection.aggregate(pipeline)
    return list(results)

def get_search_result(query, collection):

    get_knowledge = vector_search(query, collection)

    search_result = ""
    for result in get_knowledge:
        search_result += f"Lat: {result.get('lat', 'N/A')}, Lon: {result.get('lon', 'N/A')}, Description: {result.get('description', 'N/A')}\n"

    return search_result

def ask(query):
    source_information = get_search_result(query, collection)
    combined_information = f"Query: {query}\nAccording to the results, suggest the best place in response to the query:\n{source_information}."    
    return combined_information