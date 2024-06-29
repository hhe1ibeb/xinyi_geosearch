from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from src.search import collection, detect_language, vector_search
from src.chat import answer, extract_coordinates_from_url, extract_coordinates_from_suggestion
from src.evaluation import get_ranking
import json
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://10.243.8.32:5173"  # Add your frontend's address here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB client setup using environment variable
MONGODB_URI = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(MONGODB_URI)
db = client["rag_evaluation"]
evaluation_collection = db["user_choices"]

# Mount static files for serving CSS and JS
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Setup templates directory for HTML files
templates = Jinja2Templates(directory="frontend/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/ask")
async def ask(query: str):
    lang = detect_language(query)
    ans = answer(query, lang)
    if ans is not None:
        return ans
    raise HTTPException(status_code=404, detail="Suggestion not found")

@app.get("/get_results")
async def get_results(query: str):
    lang = detect_language(query)
    if lang == 'zh-tw' or lang == 'zh-cn':
        lang = 'zh'
    results = vector_search(query, collection, lang)
    suggestion = answer(query, lang)
    if results is not None:
        for result in results:
            lat, lon = extract_coordinates_from_url(result["fwd"])
            result["image_url_fwd"] = f"https://raw.githubusercontent.com/hhe1ibeb/xinyi_geosearch/main/data/photos/{lat}_{lon}_fwd.jpeg"
            result["image_url_l"] = f"https://raw.githubusercontent.com/hhe1ibeb/xinyi_geosearch/main/data/photos/{lat}_{lon}_l.jpeg"
            result["image_url_r"] = f"https://raw.githubusercontent.com/hhe1ibeb/xinyi_geosearch/main/data/photos/{lat}_{lon}_r.jpeg"
        suggest_lat, suggest_lon = extract_coordinates_from_suggestion(suggestion)
        suggestion_rank = get_ranking(results, suggest_lat, suggest_lon)
        return {"results": results, "suggestion_rank": suggestion_rank}
    raise HTTPException(status_code=404, detail="Results not found")

@app.post("/submit_choice")
async def submit_choice(query: str = Form(...), choice: int = Form(...), suggestion_rank: int = Form(...)):
    print("Received form data:")
    print("Query:", query)
    print("Choice:", choice)
    print("Suggestion Rank:", suggestion_rank)
    document = {
        "query": query,
        "choice": choice,
        "suggestion_rank": suggestion_rank
    }
    await evaluation_collection.insert_one(document)
    return {"message": "Choice submitted successfully"}