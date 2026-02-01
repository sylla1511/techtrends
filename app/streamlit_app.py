"""
We decided to create an application called TechTrends,
which is a Streamlit application focused on technology news that automatically retrieves articles from the websites Hackers News (via scraping) and dev.to (via API),
standardizes them, categorizes them by keyword, and then stores them in a SQLite database. The application has its own interface with different tabs and user interaction, 
and even allows you to create a summary with ChatGPT from within the application. It also features a word cloud.

"""
import sys
from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from wordcloud import WordCloud

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import MAX_ARTICLES_PER_SOURCE, TECH_KEYWORDS
from src.api_devto import DevToAPI
from src.data_processing import DataProcessor
from src.database import Database
from src.llm_utils import summarize_text
from src.scraper_hackernews import HackerNewsScraper
import os
from dotenv import load_dotenv

load_dotenv()

# Vérif clé OpenAI → Mode dégradé si absente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HAS_OPENAI = OPENAI_API_KEY is not None and OPENAI_API_KEY.startswith("sk-")

if not HAS_OPENAI:
    st.warning("⚠️ OpenAI non configuré → Résumés désactivés (fonctionnalités principales OK)")


# Initialization and cache

@st.cache_resource
def get_db() -> Database:
    return Database()

# Page configuration


# Custom CSS for enhanced styling

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.main {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    background-attachment: fixed;
}
[data-testid="stMetricValue"] {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
}
.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5);
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
}
h1, h2, h3 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
}
[data-testid="stSidebar"] * {
    color: white !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.25);
}
.article-card {
    background: white;
    padding: 24px;
    border-radius: 16px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    border-left: 4px solid #667eea;
}
.article-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 32px rgba(102, 126, 234, 0.25);
}
</style>
""", unsafe_allow_html=True)

# Session state initialization

if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.df = pd.DataFrame()
    st.session_state.db = get_db()
    st.session_state.last_refresh = None

# Data loading functions

@st.cache_data(show_spinner=False)
def _load_data_from_db(limit: int = 200) -> pd.DataFrame:
    """Lecture des articles depuis SQLite (mise en cache)."""
    db = get_db()
    return db.get_all_articles(limit=limit)

def load_data(use_cache: bool = True) -> pd.DataFrame:
    """Charge les données depuis les sources et/ou la base SQLite."""
    with st.spinner("Chargement des données..."):
        # 1) Try charging from the base if prompted
        if use_cache:
            df = _load_data_from_db(limit=200)
            if not df.empty:
                st.success(f"{len(df)} articles chargés depuis la base de données")
                st.session_state.last_refresh = datetime.now()
                st.session_state.df = df
                st.session_state.data_loaded = True
                return df

        # 2) Otherwise, scraping + API (more complex operation)
        st.info("Scraping Hacker News...")
        hn_scraper = HackerNewsScraper(max_articles=MAX_ARTICLES_PER_SOURCE)
        hn_articles = hn_scraper.scrape_frontpage()

        st.info("Récupération des articles Dev.to...")
        devto_api = DevToAPI(max_articles=MAX_ARTICLES_PER_SOURCE)
        devto_articles = devto_api.get_top_articles(per_page=30)

        processor = DataProcessor()
        hn_df = processor.articles_to_dataframe(hn_articles)
        devto_df = processor.articles_to_dataframe(devto_articles)

        df = processor.merge_sources(hn_df, devto_df)
        df = processor.categorize_by_keywords(df, TECH_KEYWORDS)

        # 3) Insert into DB
        if not df.empty:
            db = get_db()
            articles_list = df.to_dict("records")
            inserted = db.insert_articles(articles_list)
            st.success(f"{len(df)} articles récupérés ({inserted} nouveaux)")
            st.session_state.last_refresh = datetime.now()
            st.session_state.df = df
            st.session_state.data_loaded = True

        return df

# UI Components

def _start_card():
    st.markdown("""
    <div style="
        background: rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(8px);
    ">
    """, unsafe_allow_html=True)

def _end_card():
    st.markdown("</div>", unsafe_allow_html=True)

# Page display functions

def display_home():
    """Page d'accueil avec vue d'ensemble améliorée."""
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='font-size: 4rem; margin-bottom: 0;'>📰 TechTrends</h1>
        <p style='font-size: 1.5rem; color: #f7fafc; font-weight: 500;'>
            Analyse en temps réel des tendances technologiques
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.last_refresh:
        time_diff = datetime.now() - st.session_state.last_refresh
        minutes_ago = int(time_diff.total_seconds() / 60)
        st.markdown(
            f"""
            <div style='text-align: center; color: #e2e8f0; margin-bottom: 2rem;'>
                 Dernière mise à jour : il y a {minutes_ago} minute(s)
            </div>
            """,
            unsafe_allow_html=True,
        )

    _start_card()

# UI Buttons

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Rafraîchir les données", type="primary", use_container_width=True):
            st.session_state.df = load_data(use_cache=False)
            st.session_state.data_loaded = True
            st.rerun()
# Load from DB button
    with col2:
        if st.button("Charger depuis SQLite", use_container_width=True):
            st.session_state.df = load_data(use_cache=True)
            st.session_state.data_loaded = True
            st.rerun()
# Export buttons
    with col3:
        if not st.session_state.df.empty:
            csv = st.session_state.df.to_csv(index=False)
            st.download_button(
                label="Export CSV",
                data=csv,
                file_name=f"techtrends_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
# JSON export
    with col4:
        if not st.session_state.df.empty:
            json_data = st.session_state.df.to_json(orient="records", indent=2)
            st.download_button(
                label="Export JSON",
                data=json_data,
                file_name=f"techtrends_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True,
            )
# Summary
    if st.session_state.df.empty:
        st.markdown("""
        <div style='text-align: center; padding: 4rem 2rem; background: white; border-radius: 16px; margin: 2rem 0;'>
            <h2 style='color: #667eea;'>👋 Bienvenue sur TechTrends !</h2>
            <p style='font-size: 1.2rem; color: #4a5568; margin: 1rem 0;'>
                Commencez par cliquer sur <strong>🔄 Rafraîchir les données</strong> pour récupérer les dernières actualités tech.
            </p>
            <p style='color: #718096;'>
                 Hacker News + Dev.to |  SQLite |  Analyse NLP
            </p>
        </div>
        """, unsafe_allow_html=True)
        _end_card()
        return
# Display a dashboard summary of the dataset:
# total number of articles, number of sources and categories,
# and overall engagement (points + reactions)

    df = st.session_state.df

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total articles", f"{len(df):,}")

    with col2:
        sources = df["source"].nunique() if "source" in df.columns else 0
        st.metric("Sources", sources)

    with col3:
        if "category" in df.columns:
            categories = df["category"].nunique()
            st.metric("Catégories", categories)

    with col4:
        total_engagement = 0
        if "points" in df.columns:
            total_engagement += int(df["points"].sum())
        if "reactions" in df.columns:
            total_engagement += int(df["reactions"].sum())
        st.metric("Engagement", f"{total_engagement:,}")
        
# Visualizations 

    st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribution par source")
        if "source" in df.columns:
            source_counts = df["source"].value_counts()
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=source_counts.index,
                        values=source_counts.values,
                        hole=0.4,
                        marker=dict(colors=["#667eea", "#764ba2"]),
                    )
                ]
            )
            fig.update_layout(height=400, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
# Categories bar chart
    with col2:
        st.subheader("Top catégories")
        if "category" in df.columns:
            category_counts = df["category"].value_counts().head(8)
            fig = go.Figure(
                data=[
                    go.Bar(
                        y=category_counts.index,
                        x=category_counts.values,
                        orientation="h",
                        marker=dict(color=category_counts.values, colorscale="Viridis"),
                    )
                ]
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    _end_card()
# Display the articles page with interactive filters:
# filter by source and category, keyword search,
# and prepare the filtered dataset for display

def display_articles():
    """Page d'affichage des articles."""
    st.title("Liste des articles")

    if st.session_state.df.empty:
        st.warning("Aucune donnée disponible.")
        return

    df = st.session_state.df.copy()

    st.sidebar.subheader("Filtres")

    if "source" in df.columns:
        sources = ["Toutes"] + list(df["source"].unique())
        selected_source = st.sidebar.selectbox("Source", sources)
        if selected_source != "Toutes":
            df = df[df["source"] == selected_source]

    if "category" in df.columns:
        categories = ["Toutes"] + sorted(df["category"].unique().tolist())
        selected_category = st.sidebar.selectbox("Catégorie", categories)
        if selected_category != "Toutes":
            df = df[df["category"] == selected_category]

    search_query = st.sidebar.text_input("🔎 Rechercher", placeholder="Mot-clé...")
    if search_query:
        mask = df["title"].str.contains(search_query, case=False, na=False)
        if "description" in df.columns:
            mask |= df["description"].str.contains(search_query, case=False, na=False)
        df = df[mask]

    _start_card()
# Display the list of articles (limited to 50):
# show title, link, short description, metadata (author, source, category),
# engagement indicators (points, reactions, comments),
# and allow on-demand AI-generated summaries for each article

    st.markdown(f"### {len(df)} article(s) trouvé(s)")

    for idx, (_, row) in enumerate(df.head(50).iterrows()):
        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                title = row.get("title", "Sans titre")
                url = row.get("url", "#")
                st.markdown(f"### [{title}]({url})")

                if "description" in row and pd.notna(row["description"]):
                    st.markdown(str(row["description"])[:200] + "...")

                meta_parts = []
                if "author" in row and pd.notna(row["author"]):
                    meta_parts.append(f"{row['author']}")
                if "source" in row:
                    meta_parts.append(f"{row['source']}")
                if "category" in row and row["category"] != "Other":
                    meta_parts.append(f"{row['category']}")

                if meta_parts:
                    st.markdown(" • ".join(meta_parts))

                # Full text for the abstract
                full_text = ""
                if "description" in row and pd.notna(row["description"]):
                    full_text += str(row["description"]) + "\n\n"
                full_text += str(row.get("title", ""))

                if st.button("Résumer avec l'IA", key=f"summarize_{row.get('id', idx)}"):
                    if not HAS_OPENAI:
                       st.info("🔒 Résumé indisponible (OPENAI_API_KEY non définie).")
                    else:
                      from src.llm_utils import summarize_text
                      with st.spinner("Génération du résumé..."):
                         summary = summarize_text(full_text)
                      st.info(summary)

            with col2:
                if "points" in row and pd.notna(row["points"]) and row["points"] > 0:
                    st.metric("Points", int(row["points"]))
                if "reactions" in row and pd.notna(row["reactions"]) and row["reactions"] > 0:
                    st.metric("❤️", int(row["reactions"]))
                if "comments" in row and pd.notna(row["comments"]) and row["comments"] > 0:
                    st.metric("💬", int(row["comments"]))

            st.markdown("---")

    _end_card()
# Trends display function
def display_trends():
    """Page d'analyse des tendances."""
    st.title("Analyse des tendances")

    if st.session_state.df.empty:
        st.warning("Aucune donnée disponible.")
        return

    df = st.session_state.df
    processor = DataProcessor()

    _start_card()

    st.subheader("Nuage de mots des sujets tendances")

    trending_topics = processor.get_trending_topics(df, column="title", top_n=50)
# WordCloud generation
    if trending_topics:
        word_freq = dict(trending_topics)

        wordcloud = WordCloud(
            width=1200,
            height=600,
            background_color="white",
            colormap="viridis",
            relative_scaling=0.5,
            min_font_size=10,
        ).generate_from_frequencies(word_freq)

        fig, ax = plt.subplots(figsize=(15, 8))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        plt.tight_layout()
        st.pyplot(fig)

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top 10 mots-clés")
            for rank, (word, count) in enumerate(trending_topics[:10], 1):
                st.markdown(f"{rank}. **{word}** ({count} mentions)")

        with col2:
            st.subheader("Graphique des tendances")
            words, counts = zip(*trending_topics[:15])
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=list(counts),
                        y=list(words),
                        orientation="h",
                        marker=dict(color=list(counts), colorscale="Viridis"),
                    )
                ]
            )
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Tendances temporelles")
# Time series of articles per day
    if "published_at" in df.columns:
        # Ensure the correct format
        df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")
        df["published_date"] = df["published_at"].dt.date

        per_day = (
            df.dropna(subset=["published_date"])
            .groupby("published_date")
            .size()
            .reset_index(name="count")
        )

        if not per_day.empty:
            fig = px.line(
                per_day,
                x="published_date",
                y="count",
                markers=True,
                title="Nombre d'articles collectés par jour",
            )
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Nombre d'articles",
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas suffisamment de dates pour afficher une tendance temporelle.")
    else:
        st.info("La colonne 'published_at' est manquante dans les données.")

    _end_card()
# Stats display function
def display_stats():
    """Page de statistiques détaillées."""
    st.title("Statistiques détaillées")

    if st.session_state.df.empty:
        st.warning("Aucune donnée disponible.")
        return

    df = st.session_state.df
    processor = DataProcessor()

    stats = processor.get_statistics(df)

    _start_card()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total articles", stats.get("total_articles", 0))
        if "avg_points" in stats:
            st.metric("Points moyens", f"{stats['avg_points']:.1f}")

    with col2:
        if "total_comments" in stats:
            st.metric("Total commentaires", f"{stats['total_comments']:,}")
        if "avg_comments" in stats:
            st.metric("Commentaires moyens", f"{stats['avg_comments']:.1f}")

    with col3:
        if "total_reactions" in stats:
            st.metric("Total réactions", f"{stats['total_reactions']:,}")
        if "avg_reactions" in stats:
            st.metric("Réactions moyennes", f"{stats['avg_reactions']:.1f}")

    st.markdown("---")
    st.subheader("Top 10 articles")
# Top articles by points, comments, reactions
    tab1, tab2, tab3 = st.tabs(["Par points", "Par commentaires", "Par réactions"])

    with tab1:
        if "points" in df.columns:
            top_points = processor.get_top_articles(df, metric="points", top_n=10)
            for _, row in top_points.iterrows():
                st.markdown(f"**{row['title']}** – {int(row['points'])} points")
                st.markdown(f"[Lire l'article]({row['url']})")
                st.markdown("---")

    with tab2:
        if "comments" in df.columns:
            top_comments = processor.get_top_articles(df, metric="comments", top_n=10)
            for _, row in top_comments.iterrows():
                st.markdown(f"**{row['title']}** – {int(row['comments'])} commentaires")
                st.markdown(f"[Lire l'article]({row['url']})")
                st.markdown("---")

    with tab3:
        if "reactions" in df.columns:
            top_reactions = processor.get_top_articles(df, metric="reactions", top_n=10)
            for _, row in top_reactions.iterrows():
                st.markdown(f"**{row['title']}** – {int(row['reactions'])} réactions")
                st.markdown(f"[Lire l'article]({row['url']})")
                st.markdown("---")

    _end_card()

# Sidebar navigation

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Choisir une page",
    ["Accueil", "Articles", "Tendances", "Statistiques"],
)

if page == "Accueil":
    display_home()
elif page == "Articles":
    display_articles()
elif page == "Tendances":
    display_trends()
elif page == "Statistiques":
    display_stats()

st.sidebar.markdown("---")
st.sidebar.markdown("**TechTrends v2.0**")
st.sidebar.markdown("Projet M2 Software 2025-2026")
st.sidebar.markdown("Developed with ❤️ and Streamlit")
