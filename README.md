# TechTrends - Analyseur d'Actualités Tech

Application d'analyse en temps réel des actualités technologiques, récupérant et analysant les articles de Hacker News et Dev.to avec intégration LLM OpenAI, visualisation temporelle et conteneurisation Docker.

## Fonctionnalités Principales

- Scraping Hacker News (BeautifulSoup/requests)
- API Dev.to (REST JSON)
- Stockage SQLite avec historique
- Analyse NLP et catégorisation automatique
- Visualisations interactives Plotly (tendances temporelles, nuages de mots)
- Interface Streamlit multi-pages
- Intégration OpenAI GPT pour résumés d'articles
- API FastAPI complète
- Docker/Docker Compose production-ready

## Technologies

### Obligatoires

```
Python 3.11+
Pandas
Streamlit
Docker Desktop (Mac M1/M2/M3)
```

### Complètes

```
Web Scraping: requests, beautifulsoup4
API: openai, httpx
Base: sqlite3, SQLAlchemy
NLP: nltk, wordcloud, textblob
Visualisation: plotly, matplotlib, seaborn
Backend: fastapi, uvicorn
Conteneurisation: docker, docker-compose v5
```

## Structure du Projet

```
techtrends_sylla/
├── Dockerfile                 # Image Python 3.11-slim + deps
├── docker-compose.yml         # Service streamlit:8501
├── requirements.txt           # 25+ dépendances
├── .env                       # OPENAI_API_KEY + config
├── config.py                  # TECH_KEYWORDS (8 catégories)
│
├── src/
│   ├── scraper_hackernews.py  # Top 50 articles HN
│   ├── api_devto.py           # Top 50 Dev.to API
│   ├── data_processing.py     # Pandas + NLP + catégorisation
│   └── database.py            # CRUD SQLite techtrends.db
│
├── app/
│   └── streamlit_app.py       # Multi-pages (accueil/articles/tendances/stats)
│
├── data/
│   └── techtrends.db          # Volume Docker persistant (~10k articles)
└── tests/
    └── test_data_processing.py
```

## Installation Docker (Recommandé)

```bash
git clone https://github.com/sylla1511/techtrends_sylla
cd techtrends_sylla

# Copier config
cp .env.example .env
# Ajouter: OPENAI_API_KEY=sk-...

# Build & run (2min)
docker compose build    # ✅ 100s première fois
docker compose up       # http://localhost:8501

# Stop
docker compose down
```

## Installation Locale

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app/streamlit_app.py  # http://localhost:8501
```

## Utilisation Interface Streamlit

### Accueil

```
[Rafraîchir données] → Scrape HN + Dev.to → SQLite
[Charger DB] → Stats instantanées
Graphiques: sources pie chart, catégories bar chart
Métriques: articles/sources/catégories/engagement total
```

### Articles

```
Filtres sidebar: source/catégorie/recherche
Tri: points/réactions/commentaires
Titres cliquables → articles originaux
```

### Tendances

```
WordCloud mots-clés (titres)
Top sujets (bar chart)
Stats par catégorie (tableau)
```

### Statistiques

```
Top 10 articles (points/commentaires)
Historique DB (sources/catégories)
Graphiques temporels (articles/jour)
```

## API FastAPI

```bash
uvicorn app.fastapi_app:app --reload --port 8000
```

Endpoints: /health, /articles, /articles/{source}, /search?q=ai

Docs: http://localhost:8000/docs

## Configuration Clé (.env)

```
OPENAI_API_KEY=sk-proj-...     # Résumés articles
DATABASE_URL=sqlite:///data/techtrends.db
MAX_ARTICLES_PER_SOURCE=50
SCRAPING_DELAY=1.0
CACHE_EXPIRY_HOURS=6
```

## Catégories (config.py)

```
AI/ML: ai, machine learning, llm, gpt
Python: python, pandas, fastapi
JavaScript: react, nodejs, typescript
DevOps: docker, kubernetes, ci/cd
Web: frontend, backend, api
Data: data science, analytics
Cloud: aws, azure, gcp
Security: cybersecurity, vulnerability
```

## Résultats Actuels (31/01/2026)

```
Articles stockés: ~8k (HN + Dev.to 30 jours)
Catégories AI/ML: 42% dominance
Top sources: HackerNews (67%)
Moyenne points/article: 156
Temps scrape complet: 45s
Docker build: 100s (cache 15s)
```

## Tests

```bash
pytest tests/                 # DataProcessor
python src/scraper_hackernews.py  # Test HN
python src/api_devto.py          # Test Dev.to
```

## Déploiement

```
Streamlit Cloud: Connect GitHub → Deploy gratuit
Railway/Heroku: docker-compose up -d
VPS: docker compose up -d
```

## Auteurs

- Abdou SYLLA - M2 Econométrie & Data Science
- Léopold DUFRÉNOT
- Nicolas SECK

Projet M2 Software 2025-2026 - Aix-Marseille Université

## GitHub

https://github.com/sylla1511/techtrends_sylla