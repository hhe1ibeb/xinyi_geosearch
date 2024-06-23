from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.search import collection, detect_language, vector_search
from src.chat import answer
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
    lang = detect_language(query)
    if not lang in ['zh-tw', 'zh-cn', 'en']:
        raise HTTPException(status_code=503, detail="Language not supported")
    if lang == 'zh-tw' or lang == 'zh-cn':
        lang = 'zh'
    results = vector_search(query, collection, lang)
    results_json = json.dumps(results)
    if results is not None:
        return results
    raise HTTPException(status_code=404, detail="Results not found")

@app.get("/ask")
async def ask(query: str):
    result = answer(query, detect_language(query))
    if result is not None:
        return result
    raise HTTPException(status_code=404, detail="Item not found")