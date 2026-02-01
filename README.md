# TechTrends - Tech News Analyzer

Real-time analysis application for technology news from Hacker News and Dev.to, with OpenAI GPT-4 integration, Plotly time visualization, and production-ready Docker deployment.

## Key Features

| Module | Technology | Outcome |
|--------|------------|---------|
| HN Scraping | BeautifulSoup4 + requests | 50 top articles (title / points / URL) |
| Dev.to API | REST JSON | 50 articles with "tech" tag + reactions |
| Storage | SQLite + SQLAlchemy | 8k+ historical articles |
| NLP | NLTK + WordCloud | Automatic categorization into 8 topics |
| Visualization | Plotly + Streamlit | Real-time charts + word clouds |
| LLM | OpenAI GPT-4 | 50-word article summaries |
| API | FastAPI + Uvicorn | /articles, /search, /health |
| Docker | Python 3.11-slim | 100s build, 250MB image |

## Complete Technology Stack

```
CORE 
├── Python 3.11+ (python:3.11-slim)
├── Pandas 2.2.2 (data processing)
├── Streamlit 1.39.0 (UI multi-pages)
└── Docker Compose v5.0.1 (production)

SCRAPING 
├── requests 2.32.3
├── beautifulsoup4 4.12.3
└── openai>=1.6.0 (GPT-4 summaries)

DATA 
├── SQLAlchemy 2.0.23
├── python-dotenv 1.0.0
└── pytz 2024.2

VISUALISATION 
├── plotly 5.24.1 (temps réel)
├── matplotlib 3.9.2
├── seaborn 0.13.2
└── wordcloud 1.9.4

NLP 
├── nltk 3.8.1
└── textblob 0.17.1

TESTS 
├── pytest 7.4.3
└── pytest-cov 4.1.0
```

## Architecture Project

```
techtrends_sylla/                    # 25 files, 15MB
├── Dockerfile                      # sha256:052cfdc66930e7bdc5dce120ad4895f1e960cc8c98eb8d9622ab4b9ad402437f
├── docker-compose.yml              # Service “techtrends:8501” + 4 volumes
├── requirements.txt                # 25 dépendances pinned
├── README.md                       # Ce document
├── .env.example                    # OPENAI_API_KEY template
├── config.py                       # TECH_KEYWORDS (8 categories)
│
├── src/                           # Core business logic
│   ├── scraper_hackernews.py      # Top 50 HN (45s)
│   ├── api_devto.py               # Top 50 Dev.to API
│   ├── data_processing.py         # Pandas + NLP + categorization
│   └── database.py                # CRUD SQLite (~8k articles)
│
├── app/
│   └── streamlit_app.py           # Streamlit
│
├── data/                          # Docker volume
│   └── techtrends.db              # (10MB)
└── tests/
    └── test_data_processing.py    # pytest coverage
```

##  Docker deployment 

```bash
# Clone + config (30s)
git clone https://github.com/sylla1511/techtrends.git
cd techtrends_sylla
cp .env.example .env
echo "OPENAI_API_KEY=sk-proj-..." >> .env  ## optionnel
## 🚨 Problème conteneur (normal)
Si erreur `techtrends_app already in use` :

docker rm -f techtrends_app
docker compose up -d


# Build + run (100s first time)
docker compose build        # Image: techtrends_sylla-techtrends.git
docker compose up           # http://localhost:8501

# Production
docker compose up -d        # Background
docker compose logs -f      # Real-time logs
docker compose down         # Clean stop
```

requirements :

```
python-dotenv==1.0.0
pandas==2.2.2
numpy==1.26.4
beautifulsoup4==4.12.3
requests==2.32.3
# lxml supprimé : BeautifulSoup n'en a pas absolument besoin pour ton usage
sqlalchemy==2.0.23
nltk==3.8.1
wordcloud==1.9.4
textblob==0.17.1
matplotlib==3.9.2
seaborn==0.13.2
plotly==5.24.1
streamlit==1.39.0
pytest==7.4.3
pytest-cov==4.1.0
python-dateutil==2.9.0.post0
pytz==2024.2
fastapi==0.115.6
uvicorn==0.32.1
selenium==4.27.1
openai>=1.6.0
```
Dockerfile optimized:

```
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
EXPOSE 8501
ENV PYTHONUNBUFFERED=1
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

docker-compose.yml production :

```
services:
  techtrends:
    build: .
    container_name: techtrends_app
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data          # SQLite persistant
      - ./.env:/app/.env          # OPENAI_API_KEY
      - ./app:/app/app            # Hot reload dev
      - ./src:/app/src            # Modules Python
    environment:
      - PYTHONUNBUFFERED=1
      - ENVIRONMENT=production
    restart: unless-stopped
```

## Local Installation (Development)

```bash
# Virtual environment
python3 -m venv venv
source venv/bin/activate     # macOS/Linux
pip install --upgrade pip
pip install -r requirements.txt

# Config + NLTK
cp .env.example .env
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Run
streamlit run app/streamlit_app.py --server.port 8501
```

## Interface Streamlit (4 Pages)

### 1. Home – Metrics + Refresh

```
[Refresh data] → HN scraping (45s) + Dev.to API → SQLite
Metrics: 8k articles, 67% HN, 42% AI/ML, 156 avg points/article
Charts: Source pie chart, Category bar chart
```

### 2. Articles – Search + Filters

```
Sidebar: Source (HN/Dev.to), Category (AI/Python/DevOps), Text search
Sorting: Points / Comments / Reactions
Clickable titles → Original article
```

### 3. Trends – NLP + Visualizations

```
WordCloud: Title keywords (last 24h)
Bar chart: Top 10 topics
Table: Stats by category (articles / points / engagement)
```

### 4. Statistics – Advanced Analytics

```
Top 10 articles (points / comments)
30-day history (articles per day)
Source / category breakdown
Plotly time-series charts
```

## FastAPI API (Optional)

```bash
# Terminal 2
uvicorn app.fastapi_app:app --reload --port 8000
```

Endpoints :

```
GET /health                    # Status OK
GET /articles?limit=50         # Derniers articles JSON
GET /articles/source/HackerNews # Filtre source
GET /search?q=python           # Recherche full-text
```

Docs auto : http://localhost:8000/docs | http://localhost:8000/redoc

## Configuration (.env)

```
# OpenAI (obligatoire pour résumés)
OPENAI_API_KEY=sk-proj-your-key-here

# Base de données
DATABASE_URL=sqlite:///data/techtrends.db

# Scraping
MAX_ARTICLES_PER_SOURCE=50
SCRAPING_DELAY=1.0
CACHE_EXPIRY_HOURS=6

# Logs
LOG_LEVEL=INFO
ENVIRONMENT=production
```

## Automatic Categories (config.py)

```python
TECH_KEYWORDS = {
    "AI/ML": ["ai", "llm", "gpt", "machine learning", "deep learning"],
    "Python": ["python", "pandas", "fastapi", "django", "flask"],
    "JavaScript": ["react", "nodejs", "typescript", "vue", "angular"],
    "DevOps": ["docker", "kubernetes", "ci/cd", "terraform", "jenkins"],
    "Web": ["frontend", "backend", "api", "graphql", "web development"],
    "Data": ["data science", "analytics", "visualization", "big data"],
    "Cloud": ["aws", "azure", "gcp", "serverless", "cloud"],
    "Security": ["cybersecurity", "vulnerability", "encryption", "penetration"]
}
```

## Performances (31/01/2026)

```
SQLite database: 8,247 articles (last 30 days)
AI/ML dominance: 42% of articles
HackerNews: 67% vs Dev.to 33%
Average score: 156 per article
Full scraping time: 45 seconds
Docker build: 100s (15s with cache)
Image size: 250MB (optimized python:3.11-slim)
```

## Unit Tests

```bash
# Complete coverage
pytest tests/ --cov=src/ --cov-report=html

# Individual tests
python src/scraper_hackernews.py    # Vérif HN live
python src/api_devto.py             # Vérif Dev.to API
```

## Production Deployment

### Streamlit Cloud (Free)

- Connect GitHub repo
- requirements.txt + .streamlit/config.toml
- Deploy auto → URL publique

### Railway/Heroku

```bash
railway up                    # Auto-detect Docker
# or
heroku container:push web     # Dockerfile
```

### VPS Ubuntu

```bash
git clone https://github.com/sylla1511/techtrends.git
cd techtrends_sylla
docker compose up -d
# Accès: http://IP_SERVEUR:8501
```

## Common Troubleshooting

| Issue | Solution |
|------|----------|
| docker: command not found | Open a new terminal or run `source ~/.zshrc` |
| Container name already in use | `docker compose down` |
| OPENAI_API_KEY missing | `cp .env.example .env` + add your key |
| Port 8501 already in use | `docker compose down` or use `--port 8502` |
| NLTK data missing | `python -c "import nltk; nltk.download('punkt')"` |
| Slow build (100s+) | Normal the first time, ~15s afterwards (cache) |

## AMETICE Project Submission


```
Archive: techtrends_sylla_v2.0.tar.gz (15MB)
GitHub: https://github.com/sylla1511/techtrends
Docker SHA: sha256:052cfdc66930e7bdc5dce120ad4895f1e960cc8c98eb8d9622ab4b9ad402437f
Authors: Abdou SYLLA, Léopold DUFRÉNOT, Nicolas SECK
M2 Econométrie & Data Science 2025-2026
Aix-Marseille University
```

## Authors

| Name | Role | Contribution |
|-----|------|--------------|
| Abdou SYLLA | Lead Dev | Architecture, Docker, Streamlit, GitHub |
| Léopold DUFRÉNOT | Data/NLP | Scraping HN, Data Processing, Catégorisation |
| Nicolas SECK | Backend/ML | OpenAI GPT, FastAPI, Tests unitaires |

Projet M2 Software 2025-2026 - Aix-Marseille Université
