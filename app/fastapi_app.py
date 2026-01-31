"""
We decided to use the quick API, the API that allows articles to be exposed,
as recommended in the guidelines. 
"""
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.database import Database

app = FastAPI(title="TechTrends API", version="1.0.0")
db = Database()

# Health check endpoint 

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "message": "TechTrends API is running"}

# Endpoint to get a list of articles
@app.get("/articles", response_model=List[Dict[str, Any]])
def get_articles(limit: int = 50) -> List[Dict[str, Any]]:
    df = db.get_all_articles(limit=limit)
    return df.to_dict(orient="records")


@app.get("/articles/source/{source_name}", response_model=List[Dict[str, Any]])
def get_articles_by_source(source_name: str, limit: int = 50) -> List[Dict[str, Any]]:
    df = db.get_articles_by_source(source_name)
    if df.empty:
        raise HTTPException(status_code=404, detail="No articles for this source")
    return df.head(limit).to_dict(orient="records")

# Endpoint to search articles

@app.get("/search")
def search_articles(q: str) -> Dict[str, Any]:
    df = db.search_articles(q)
    return {
        "query": q,
        "count": len(df),
        "results": df.head(50).to_dict(orient="records"),
    }
