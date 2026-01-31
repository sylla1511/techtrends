import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# Configuration for TechTrends application
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

APP_NAME = os.getenv("APP_NAME", "TechTrends")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/techtrends.db")
SQLITE_PATH = DATA_DIR / "techtrends.db"

MAX_ARTICLES_PER_SOURCE = int(os.getenv("MAX_ARTICLES_PER_SOURCE", "50"))
SCRAPING_DELAY = float(os.getenv("SCRAPING_DELAY", "1.0"))
CACHE_EXPIRY_HOURS = int(os.getenv("CACHE_EXPIRY_HOURS", "6"))

TECH_KEYWORDS = {
    "AI": ["ai", "artificial intelligence", "machine learning", "deep learning", "llm", "gpt", "chatgpt"],
    "Python": ["python", "django", "flask", "fastapi", "pandas", "numpy"],
    "JavaScript": ["javascript", "nodejs", "react", "vue", "angular", "typescript"],
    "DevOps": ["docker", "kubernetes", "ci/cd", "jenkins", "github actions", "terraform"],
    "Web": ["web development", "frontend", "backend", "api", "rest", "graphql"],
    "Data": ["data science", "data analysis", "big data", "analytics", "visualization"],
    "Cloud": ["aws", "azure", "gcp", "cloud computing", "serverless"],
    "Security": ["cybersecurity", "security", "encryption", "vulnerability", "penetration testing"],
}
