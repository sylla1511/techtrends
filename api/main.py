from fastapi import FastAPI
from typing import List, Dict, Any

from src.database import Database
from src.data_processing import DataProcessor

# Initializing the FastAPI application
app = FastAPI(
    title="TechTrends API",
    description="API REST pour exposer les articles et statistiques TechTrends",
    version="1.0.0",
)

db = Database()
processor = DataProcessor()

# Endpoint to get a list of articles

@app.get("/articles", summary="Lister les articles")
def get_articles(limit: int = 50) -> List[Dict[str, Any]]:
    df = db.get_all_articles(limit=limit)
    return df.to_dict(orient="records")


@app.get("/stats", summary="Statistiques globales")
def get_stats() -> Dict[str, Any]:
    df = db.get_all_articles(limit=500)
    stats = processor.get_statistics(df)
    return stats
