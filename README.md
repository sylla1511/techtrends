# 📰 TechTrends - Analyseur d'Actualités Tech

Application d'analyse en temps (quasi) réel des actualités technologiques, récupérant et analysant les articles de **Hacker News** et **Dev.to**.

---

## 🎯 L'application

- 🔍 **Scrape** Hacker News (BeautifulSoup / requests)
- 📡 **Récupère** les articles de Dev.to (API REST)
- 💾 **Stocke** les données dans une base SQLite
- 📊 **Analyse** les tendances avec Pandas et NLP simple
- 📈 **Visualise** les données avec Streamlit (Plotly, Matplotlib)
- ⚙️ **Expose** une API FastAPI sur la base d'articles
- 🐳 **Est conteneurisée** avec Docker / Docker Compose

---

## 🛠️ Technologies

### Obligatoires
- **Python 3.11**
- **Pandas**
- **Streamlit**
- **Docker** (Docker Desktop sur Mac M1)

### Utilisées dans le projet
- **Web Scraping**: requests, beautifulsoup4 (Hacker News)
- **API externes**: Dev.to (REST JSON)
- **Base de données**: SQLite (module sqlite3, accès via Database)
- **NLP / texte**: nettoyage, fréquences, WordCloud (wordcloud)
- **Visualisation**: Plotly, Matplotlib, Seaborn, Streamlit
- **API backend**: FastAPI + Uvicorn
- **Conteneurisation**: Docker, Docker Compose

---

## 📁 Structure du projet

```
techtrends/
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── .env.example
├── .env
├── config.py
│
├── src/
│   ├── __init__.py
│   ├── scraper_hackernews.py   # Scraping Hacker News
│   ├── api_devto.py            # API Dev.to
│   ├── data_processing.py      # Traitement / analyse (Pandas, NLP)
│   └── database.py             # Gestion SQLite
│
├── app/
│   ├── streamlit_app.py        # Application Streamlit
│   └── fastapi_app.py          # API FastAPI
│
├── data/
│   ├── raw/                    # (optionnel) données brutes
│   ├── processed/              # (optionnel) données traitées
│   └── techtrends.db           # Base SQLite (créée automatiquement)
│
└── tests/
    └── test_data_processing.py # Tests unitaires
```

---

## 🔧 Configuration

### Variables d'environnement (.env)

Fichier `.env.example` (à copier en `.env`) :

```env
APP_NAME=TechTrends
APP_VERSION=1.0.0
ENVIRONMENT=development

DATABASE_URL=sqlite:///data/techtrends.db
MAX_ARTICLES_PER_SOURCE=50
SCRAPING_DELAY=1.0
CACHE_EXPIRY_HOURS=6

LOG_LEVEL=INFO
```

Copie :
```bash
cp .env.example .env
```

### Catégorisation des articles (config.py)

Les catégories sont définies par des mots-clés dans `TECH_KEYWORDS` :

```python
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
```

---

## 🚀 Installation (sans Docker)

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-username/techtrends.git
cd techtrends
```

### 2. Créer l'environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate   # macOS / Linux
# ou sur Windows : venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Préparer .env

```bash
cp .env.example .env
# ajuster si besoin
```

### 5. Télécharger les ressources NLTK (si nécessaire)

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

---

## ▶️ Lancement de l'application Streamlit

Toujours dans l'environnement virtuel :

```bash
streamlit run app/streamlit_app.py
```

Puis ouvrir dans le navigateur :
```
http://localhost:8501
```

---

## 🧑‍💻 Utilisation de l'interface Streamlit

### Page 🏠 Accueil

**Bouton "🔄 Rafraîchir les données"** :
- Scrape Hacker News
- Récupère les top articles Dev.to
- Fusionne, catégorise, enregistre dans SQLite

**Bouton "💾 Charger depuis la base"** : recharge les derniers articles déjà stockés.

**Affiche** :
- Nombre total d'articles
- Nombre de sources
- Nombre de catégories
- Engagement total (points + réactions)

**Graphiques** :
- Pie chart par source
- Bar chart top catégories

---

### Page 📄 Articles

**Filtres dans la sidebar** :
- Source
- Catégorie
- Recherche texte (titre + description)

**Tri par** :
- Points, réactions, commentaires

**Affichage** :
- Titre cliquable vers l'article original
- Description courte
- Auteur, source, catégorie
- Métriques (points, réactions, commentaires)

---

### Page 📊 Tendances

- Extraction des mots-clés à partir des titres (`DataProcessor.get_trending_topics`)
- Nuage de mots (WordCloud) des sujets les plus fréquents
- Liste des top mots-clés + bar chart des top sujets
- Tableau de stats par catégorie (nombre d'articles, points, commentaires)

---

### Page 📈 Statistiques

**Indicateurs globaux** :
- Articles totaux
- Points / réactions / commentaires moyens et totaux (si disponibles)

**Top 10 articles** :
- Par points
- Par commentaires
- Par réactions

**Statistiques base de données** :
- Total par source
- Total par catégorie
- Date du dernier article

**Historique des recherches** (si `search_articles` est utilisé)

---

## 🌐 API FastAPI

L'API repose sur la même base SQLite (module `Database`).

### Lancement de l'API

Dans un terminal avec l'environnement activé :

```bash
uvicorn app.fastapi_app:app --reload --port 8000
```

### Endpoints principaux

#### `GET /health`
Vérifie que l'API tourne.

#### `GET /articles?limit=50`
Renvoie les derniers articles en JSON.

#### `GET /articles/source/{source_name}?limit=50`
Filtre par source (ex: `HackerNews`, `Dev.to`).

#### `GET /search?q=python`
Recherche d'articles par mot-clé (titre + description).

### Documentation interactive

- **Swagger UI** : http://localhost:8000/docs
- **OpenAPI** : http://localhost:8000/openapi.json

---

## 🐳 Docker / Docker Compose

### Build de l'image

À la racine du projet (pas besoin du venv) :

```bash
docker compose build
```

### Lancement du conteneur

```bash
docker compose up
```

**Accès Streamlit** : http://localhost:8501

Les données SQLite sont montées dans le volume `./data/` sur l'hôte.

### Pour arrêter

```bash
Ctrl + C
docker compose down
```

---

## 🧪 Tests

Un exemple de fichier `tests/test_data_processing.py` (simplifié) :

```python
import pandas as pd
from src.data_processing import DataProcessor

def test_articles_to_dataframe_basic():
    processor = DataProcessor()
    articles = [
        {"title": "Test 1", "points": 10, "source": "HackerNews"},
        {"title": "Test 2", "points": 20, "source": "Dev.to"},
    ]
    df = processor.articles_to_dataframe(articles)
    assert len(df) == 2
    assert "title" in df.columns
    assert df["points"].sum() == 30

def test_categorize_by_keywords():
    processor = DataProcessor()
    df = pd.DataFrame(
        [{"title": "Python for Data Science"}, {"title": "Docker for DevOps"}]
    )
    keywords = {
        "Python": ["python"],
        "DevOps": ["docker"],
    }
    df_cat = processor.categorize_by_keywords(df, keywords)
    assert set(df_cat["category"]) == {"Python", "DevOps"}
```

### Lancer les tests

```bash
pytest tests/
```

---

## 👥 Auteurs

- **Nom 1** - M2 Econométrie & Data Science - Université d'Aix-Marseille
- **Nom 2** - M2 Econométrie & Data Science - Université d'Aix-Marseille

*Projet réalisé dans le cadre du Projet M2 Software 2025-2026*

---

## 🔗 Lien GitHub

Repository : [https://github.com/votre-username/techtrends](https://github.com/votre-username/techtrends)

---

**Développé avec ❤️ pour le Projet M2 Software**


TechTrends est une application complète qui :
- 🔍 **Scrape** les articles de Hacker News avec BeautifulSoup
- 📡 **Récupère** les articles de Dev.to via leur API REST
- 💾 **Stocke** les données dans une base SQLite
- 📊 **Analyse** les tendances avec Pandas et NLP
- 📈 **Visualise** les données avec Streamlit, Plotly et Matplotlib
- 🐳 **Conteneurise** l'application avec Docker

## 🛠️ Technologies Utilisées

### Technologies Obligatoires
- ✅ **Python 3.11+** - Langage principal
- ✅ **Pandas** - Manipulation et analyse de données
- ✅ **Docker** - Conteneurisation
- ✅ **Streamlit** - Interface utilisateur interactive

### Technologies Supplémentaires
- ✅ **Web Scraping** - BeautifulSoup4 (Hacker News)
- ✅ **API Externes** - Dev.to API REST
- ✅ **Base de données** - SQLite avec SQLAlchemy
- ✅ **NLP/Analyse de texte** - NLTK, WordCloud, TextBlob
- ✅ **Visualisation** - Matplotlib, Seaborn, Plotly

### Bibliothèques Python
```
beautifulsoup4==4.12.2
requests==2.31.0
pandas==2.1.4
streamlit==1.29.0
plotly==5.18.0
matplotlib==3.8.2
seaborn==0.13.0
nltk==3.8.1
wordcloud==1.9.3
sqlalchemy==2.0.23
```

## 📁 Structure du Projet

```
techtrends/
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── .env.example
├── config.py
│
├── src/
│   ├── __init__.py
│   ├── scraper_hackernews.py   # Scraping Hacker News
│   ├── api_devto.py             # API Dev.to
│   ├── data_processing.py       # Traitement Pandas
│   └── database.py              # Gestion SQLite
│
├── app/
│   └── streamlit_app.py         # Application Streamlit
│
├── data/
│   ├── raw/                     # Données brutes
│   ├── processed/               # Données traitées
│   └── techtrends.db            # Base SQLite
│
└── tests/
    └── test_data_processing.py  # Tests unitaires
```

## 🚀 Installation et Lancement

### Option 1 : Avec Docker (Recommandé)

#### Étape 1 : Cloner le repository
```bash
git clone https://github.com/votre-username/techtrends.git
cd techtrends
```

#### Étape 2 : Créer le fichier .env (optionnel)
```bash
cp .env.example .env
# Éditer .env si nécessaire
```

#### Étape 3 : Build et lancement avec Docker Compose
```bash
# Build l'image Docker
docker-compose build

# Lancer l'application
docker-compose up
```

#### Étape 4 : Accéder à l'application
Ouvrir votre navigateur : **http://localhost:8501**

#### Arrêter l'application
```bash
docker-compose down
```

### Option 2 : Sans Docker (Développement local)

#### Étape 1 : Cloner le repository
```bash
git clone https://github.com/votre-username/techtrends.git
cd techtrends
```

#### Étape 2 : Créer un environnement virtuel
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### Étape 3 : Installer les dépendances
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Étape 4 : Télécharger les ressources NLTK
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

#### Étape 5 : Lancer l'application
```bash
streamlit run app/streamlit_app.py
```

#### Étape 6 : Accéder à l'application
Ouvrir votre navigateur : **http://localhost:8501**

## 📖 Guide d'Utilisation

### 1. Page d'Accueil 🏠
- Cliquez sur **"Rafraîchir les données"** pour scraper les derniers articles
- Consultez les métriques clés (nombre d'articles, sources, engagement)
- Visualisez les graphiques de distribution

### 2. Page Articles 📄
- Parcourez la liste complète des articles
- Utilisez les filtres (source, catégorie, recherche)
- Triez par points, réactions ou commentaires
- Cliquez sur les titres pour accéder aux articles originaux

### 3. Page Tendances 📊
- Visualisez le nuage de mots des sujets tendances
- Identifiez les top mots-clés du moment
- Analysez la distribution par catégorie

### 4. Page Statistiques 📈
- Consultez les statistiques détaillées
- Découvrez les top articles par métrique
- Accédez à l'historique de la base de données

## 🔧 Configuration

### Variables d'Environnement (.env)
```env
APP_NAME=TechTrends
APP_VERSION=1.0.0
ENVIRONMENT=development

DATABASE_URL=sqlite:///data/techtrends.db
MAX_ARTICLES_PER_SOURCE=50
SCRAPING_DELAY=1.0
CACHE_EXPIRY_HOURS=6

LOG_LEVEL=INFO
```

### Personnalisation des Catégories (config.py)
Modifiez le dictionnaire `TECH_KEYWORDS` pour ajuster les catégories :
```python
TECH_KEYWORDS = {
    "AI": ["ai", "artificial intelligence", "machine learning"],
    "Python": ["python", "django", "flask"],
    "JavaScript": ["javascript", "react", "vue"],
    # Ajoutez vos propres catégories...
}
```

## 🧪 Tests

### Lancer les tests unitaires
```bash
pytest tests/
```

### Tester un module individuellement
```bash
# Tester le scraper Hacker News
python src/scraper_hackernews.py

# Tester l'API Dev.to
python src/api_devto.py

# Tester le traitement de données
python src/data_processing.py

# Tester la base de données
python src/database.py
```

## 📊 Fonctionnalités Principales

### 1. Web Scraping (BeautifulSoup)
- Scraping éthique de Hacker News
- Respect des délais entre requêtes
- Gestion des erreurs et timeout
- Extraction de : titre, URL, points, commentaires, auteur

### 2. API REST (Dev.to)
- Récupération des articles récents
- Filtrage par tags
- Articles populaires
- Données : titre, description, réactions, temps de lecture

### 3. Base de Données SQLite
- Stockage persistant des articles
- Index optimisés pour les requêtes
- Historique des recherches
- Statistiques agrégées

### 4. Traitement NLP
- Extraction de mots-clés
- Catégorisation automatique
- Analyse de fréquence
- Génération de nuages de mots

### 5. Visualisations Interactives
- Graphiques en barres (Plotly)
- Graphiques circulaires (distribution)
- Nuages de mots (WordCloud)
- Tableaux de données interactifs

## 🐛 Dépannage

### Erreur : "ModuleNotFoundError"
```bash
# Vérifier que vous êtes dans le bon environnement
source venv/bin/activate
pip install -r requirements.txt
```

### Erreur : Port 8501 déjà utilisé
```bash
# Utiliser un port différent
streamlit run app/streamlit_app.py --server.port 8502
```

### Erreur : Docker ne se lance pas
```bash
# Vérifier que Docker est lancé
docker --version

# Reconstruire l'image
docker-compose build --no-cache
docker-compose up
```

### Erreur : Base de données verrouillée
```bash
# Supprimer la base et recommencer
rm data/techtrends.db
```

## 📦 Déploiement

### Sur Streamlit Cloud (Gratuit)
1. Créer un compte sur [streamlit.io/cloud](https://streamlit.io/cloud)
2. Connecter votre repository GitHub
3. Déployer l'application
4. Accès public : `https://votre-app.streamlit.app`

### Sur Heroku
```bash
# Installer Heroku CLI
heroku login
heroku create techtrends-app
git push heroku main
```

### Sur un serveur (VPS)
```bash
# Sur le serveur
git clone https://github.com/votre-username/techtrends.git
cd techtrends
docker-compose up -d
```

## 📝 TODO / Améliorations Futures

- [ ] Ajouter Selenium pour scraper des sites dynamiques
- [ ] Implémenter un système de notifications
- [ ] Ajouter des graphiques de tendances temporelles
- [ ] Intégrer un LLM pour résumer les articles
- [ ] Créer une API FastAPI
- [ ] Ajouter plus de sources (Reddit, Medium)
- [ ] Système de recommandation ML
- [ ] Export en PDF des rapports

## 🤝 Contribution

Contributions bienvenues ! Pour contribuer :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est réalisé dans le cadre du **Projet M2 Software 2025-2026** - Université d'Aix-Marseille.

## 📧 Contact

Pour toute question sur le projet :
- 📧 Email : virgile.pesce@univ-amu.fr
- 🔗 GitHub1 : [https://github.com/sylla1511/techtrends](https://github.com/sylla1511/techtrends)
- 🔗 GitHub2 : [https://github.com/leoco112/techtrends](https://github.com/leoco112/techtrends)
- 🔗 GitHub3 : [https://github.com/Nicolas-SECK/techtrends](https://github.com/Nicolas-SECK/techtrends)
---

**Développé avec par [Leopold DUFRENOT, Nicolas SEck et Abdou SYLLA] - Projet M2 Software 2025-2026**