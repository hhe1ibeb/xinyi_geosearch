from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from search import collection
from search import vector_search, ask
import json

app = FastAPI()

# Define Schema
class Coord(BaseModel):
    lat: float
    lon: float
    description: str

@app.get("/")
async def read_root():
    return {"Hello" : "FastAPI"}

@app.get("/get_results")
async def get_results(query: str):
    results = vector_search(query, collection)
    results_json = json.dumps(results)
    if results is not None:
        return results
    raise HTTPException(status_code=404, detail="Results not found")

@app.get("/ask")
async def ask(query: str):
    result = ask(query)
    if result is not None:
        return result
    raise HTTPException(status_code=404, detail="Item not found")