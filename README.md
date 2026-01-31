# TechTrends - Analyseur d'Actualités Tech

Application d'analyse temps réel des actualités technologiques depuis Hacker News et Dev.to, avec intégration OpenAI GPT-4, visualisation temporelle Plotly et déploiement Docker production-ready.

## Fonctionnalités Principales

| Module | Technologie | Résultat |
|--------|-------------|----------|
| Scraping HN | BeautifulSoup4 + requests | 50 top articles (titre/points/URL) |
| API Dev.to | REST JSON | 50 articles tag "tech" + réactions |
| Stockage | SQLite + SQLAlchemy | 8k+ articles historiques |
| NLP | NLTK + WordCloud | Catégorisation auto 8 thèmes |
| Visualisation | Plotly + Streamlit | Graphs temps réel + nuages mots |
| LLM | OpenAI GPT-4 | Résumés articles 50 mots |
| API | FastAPI + Uvicorn | /articles, /search, /health |
| Docker | Python 3.11-slim | Build 100s, 250MB image |

## Technologies Stack Complet

```
CORE ✅
├── Python 3.11+ (python:3.11-slim)
├── Pandas 2.2.2 (data processing)
├── Streamlit 1.39.0 (UI multi-pages)
└── Docker Compose v5.0.1 (production)

SCRAPING ✅
├── requests 2.32.3
├── beautifulsoup4 4.12.3
└── openai>=1.6.0 (GPT-4 summaries)

DATA ✅
├── SQLAlchemy 2.0.23
├── python-dotenv 1.0.0
└── pytz 2024.2

VISUALISATION ✅
├── plotly 5.24.1 (temps réel)
├── matplotlib 3.9.2
├── seaborn 0.13.2
└── wordcloud 1.9.4

NLP ✅
├── nltk 3.8.1
└── textblob 0.17.1

TESTS ✅
├── pytest 7.4.3
└── pytest-cov 4.1.0
```

## Architecture Projet

```
techtrends_sylla/                    # 25 fichiers, 15MB
├── Dockerfile                      # sha256:052cfdc66930e7bdc5dce120ad4895f1e960cc8c98eb8d9622ab4b9ad402437f
├── docker-compose.yml              # Service "techtrends:8501" + 4 volumes
├── requirements.txt                # 25 dépendances pinned
├── README.md                       # Ce document
├── .env.example                    # OPENAI_API_KEY template
├── config.py                       # TECH_KEYWORDS (8 catégories)
│
├── src/                           # Core business logic
│   ├── scraper_hackernews.py      # Top 50 HN (45s)
│   ├── api_devto.py               # Top 50 Dev.to API
│   ├── data_processing.py         # Pandas + NLP + catégorisation
│   └── database.py                # CRUD SQLite (~8k articles)
│
├── app/
│   └── streamlit_app.py           # 4 pages Streamlit
│
├── data/                          # Docker volume
│   └── techtrends.db              # Persistant (~10MB)
└── tests/
    └── test_data_processing.py    # pytest coverage
```

## 🚀 Déploiement Docker 

```bash
# Clone + config (30s)
git clone https://github.com/sylla1511/techtrends_sylla
cd techtrends_sylla
cp .env.example .env
echo "OPENAI_API_KEY=sk-proj-..." >> .env

# Build + run (100s première fois)
docker compose build        # Image: techtrends_sylla-techtrends
docker compose up           # http://localhost:8501

# Production
docker compose up -d        # Background
docker compose logs -f      # Logs temps réel
docker compose down         # Stop propre
```

Dockerfile optimisé :

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

## 💻 Installation Locale (Développement)

```bash
# Environnement virtuel
python3 -m venv venv
source venv/bin/activate     # macOS/Linux
pip install --upgrade pip
pip install -r requirements.txt

# Config + NLTK
cp .env.example .env
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Lancer
streamlit run app/streamlit_app.py --server.port 8501
```

## 🖥️ Interface Streamlit (4 Pages)

### 1. Accueil - Métriques + Rafraîchissement

```
[Rafraîchir données] → HN scrape (45s) + Dev.to API → SQLite
Métriques: 8k articles, 67% HN, 42% AI/ML, 156 pts/article moyen
Graphs: Pie chart sources, Bar chart catégories
```

### 2. Articles - Recherche + Filtres

```
Sidebar: Source (HN/Dev.to), Catégorie (AI/Python/DevOps), Recherche texte
Tri: Points/Commentaires/Réactions
Titres cliquables → Article original
```

### 3. Tendances - NLP + Visualisations

```
WordCloud: Mots-clés titres (24h)
Bar chart: Top 10 sujets
Tableau: Stats par catégorie (articles/points/engagement)
```

### 4. Statistiques - Analytics avancées

```
Top 10 articles (points/commentaires)
Historique 30 jours (articles/jour)
Sources/catégories breakdown
Graphiques temporels Plotly
```

## 🔌 API FastAPI (Optionnelle)

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

## ⚙️ Configuration (.env)

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

## 🏷️ Catégories Automatiques (config.py)

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

## 📊 Performances (31/01/2026)

```
Base SQLite: 8,247 articles (30 derniers jours)
Dominance AI/ML: 42% des articles
HackerNews: 67% vs Dev.to 33%
Points moyens: 156/article
Temps scrape complet: 45 secondes
Docker build: 100s (15s cache)
Image size: 250MB (python:3.11-slim optimisé)
```

## 🧪 Tests Unitaires

```bash
# Coverage complet
pytest tests/ --cov=src/ --cov-report=html

# Tests individuels
python src/scraper_hackernews.py    # Vérif HN live
python src/api_devto.py             # Vérif Dev.to API
```

## ☁️ Déploiement Production

### Streamlit Cloud (Gratuit)

- Connect GitHub repo
- requirements.txt + .streamlit/config.toml
- Deploy auto → URL publique

### Railway/Heroku

```bash
railway up                    # Auto-detect Docker
# ou
heroku container:push web     # Dockerfile
```

### VPS Ubuntu

```bash
git clone https://github.com/sylla1511/techtrends_sylla
cd techtrends_sylla
docker compose up -d
# Accès: http://IP_SERVEUR:8501
```

## 🐛 Dépannage Courant

| Problème | Solution |
|----------|----------|
| docker: command not found | Nouveau terminal ou source ~/.zshrc |
| Container name already in use | docker compose down |
| OPENAI_API_KEY missing | cp .env.example .env + clé |
| Port 8501 already used | docker compose down ou --port 8502 |
| NLTK data missing | python -c "import nltk; nltk.download('punkt')" |
| Build lent (100s+) | Normal première fois, 15s après (cache) |

## 📋 Rendu Projet AMETICE

```
📦 Archive: techtrends_sylla_v2.0.tar.gz (15MB)
🔗 GitHub: https://github.com/sylla1511/techtrends_sylla
🐳 Docker SHA: sha256:052cfdc66930e7bdc5dce120ad4895f1e960cc8c98eb8d9622ab4b9ad402437f
👥 Auteurs: Abdou SYLLA, Léopold DUFRÉNOT, Nicolas SECK
📚 M2 Econométrie & Data Science 2025-2026
🏫 Aix-Marseille Université
```

## 👥 Auteurs

| Nom | Rôle | Contribution |
|-----|------|--------------|
| Abdou SYLLA | Lead Dev | Architecture, Docker, Streamlit, GitHub |
| Léopold DUFRÉNOT | Data/NLP | Scraping HN, Data Processing, Catégorisation |
| Nicolas SECK | Backend/ML | OpenAI GPT, FastAPI, Tests unitaires |

Projet M2 Software 2025-2026 - Aix-Marseille Université
