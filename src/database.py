"""

This module manages the SQLite database used for TechTrends. 
First, it initializes the database schema, manages the insertion of cleaned articles,
allows articles to be retrieved and filtered, stores history, and calculates statistics.
"""
import sqlite3
import pandas as pd
from typing import List, Dict, Optional, Any
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database management class
class Database:
    """Classe pour gérer la base de données SQLite"""

    def __init__(self, db_path: str = "data/techtrends.db"):
        """
        Args:
            db_path: Chemin vers le fichier de base de données
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # Connexion / init 

    def _get_connection(self) -> sqlite3.Connection:
        """Retourne une nouvelle connexion SQLite"""
        return sqlite3.connect(str(self.db_path))

    def _init_db(self):
        """Crée les tables si elles n'existent pas"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Table of contents articles
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE,
                    source TEXT NOT NULL,
                    author TEXT,
                    description TEXT,
                    published_at TEXT,
                    scraped_at TEXT,
                    points INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    reactions INTEGER DEFAULT 0,
                    reading_time INTEGER DEFAULT 0,
                    category TEXT,
                    tags TEXT,
                    UNIQUE(title, source)
                )
                """
            )

            # Search table (history)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    results_count INTEGER
                )
                """
            )

            # Index
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON articles(source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON articles(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_published_at ON articles(published_at)")

            conn.commit()
            conn.close()
            logger.info("Database tables created successfully")

        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

    # Helpers 

    @staticmethod
    def _to_str_date(value: Any) -> Optional[str]:
        """
        Convertit un Timestamp / datetime / str en chaîne ou None
        """
        if value is None:
            return None
        if str(value) in ("NaT", "nan"):
            return None
        try:
            # Pandas Timestamp ou datetime
            return value.isoformat()
        except Exception:
            return str(value)

    # Insert 

    def insert_articles(self, articles: List[Dict[str, Any]]) -> int:
        """
        Insère des articles

        Returns:
            Nombre d'articles insérés
        """
        if not articles:
            return 0

        conn = self._get_connection()
        cursor = conn.cursor()
        inserted = 0

        try:
            for article in articles:
                try:
                    tags = article.get("tags", [])
                    if isinstance(tags, list):
                        tags = ",".join(tags)

                    pub_raw = article.get("published_at") or article.get("fetched_at")
                    scraped_raw = article.get("scraped_at")

                    pub_date = self._to_str_date(pub_raw)
                    scraped_date = self._to_str_date(scraped_raw)

                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO articles
                        (title, url, source, author, description, published_at,
                         scraped_at, points, comments, reactions, reading_time,
                         category, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            article.get("title", ""),
                            article.get("url", ""),
                            article.get("source", ""),
                            article.get("author", ""),
                            article.get("description", ""),
                            pub_date,
                            scraped_date,
                            article.get("points", 0),
                            article.get("comments", 0),
                            article.get("reactions", 0),
                            article.get("reading_time", 0),
                            article.get("category", ""),
                            tags,
                        ),
                    )

                    if cursor.rowcount > 0:
                        inserted += 1

                except sqlite3.IntegrityError:
                    # duplicate
                    continue
                except Exception as e:
                    logger.warning(f"Error inserting article: {e}")
                    continue

            conn.commit()
            logger.info(f"Inserted {inserted} new articles into database")
            return inserted

        except Exception as e:
            logger.error(f"Error inserting articles: {e}")
            conn.rollback()
            return 0

        finally:
            conn.close()

    # Selects

    def get_all_articles(self, limit: Optional[int] = None) -> pd.DataFrame:
        """Récupère tous les articles"""
        try:
            conn = self._get_connection()
            query = "SELECT * FROM articles ORDER BY published_at DESC"
            if limit:
                query += f" LIMIT {limit}"

            df = pd.read_sql_query(query, conn)
            conn.close()
            logger.info(f"Retrieved {len(df)} articles from database")
            return df

        except Exception as e:
            logger.error(f"Error retrieving articles: {e}")
            return pd.DataFrame()

    def get_articles_by_source(self, source: str) -> pd.DataFrame:
        """Récupère les articles d'une source"""
        try:
            conn = self._get_connection()
            query = "SELECT * FROM articles WHERE source = ? ORDER BY published_at DESC"
            df = pd.read_sql_query(query, conn, params=(source,))
            conn.close()
            return df
        except Exception as e:
            logger.error(f"Error retrieving articles by source: {e}")
            return pd.DataFrame()

    def get_articles_by_category(self, category: str) -> pd.DataFrame:
        """Récupère les articles d'une catégorie"""
        try:
            conn = self._get_connection()
            query = "SELECT * FROM articles WHERE category = ? ORDER BY published_at DESC"
            df = pd.read_sql_query(query, conn, params=(category,))
            conn.close()
            return df
        except Exception as e:
            logger.error(f"Error retrieving articles by category: {e}")
            return pd.DataFrame()

    def search_articles(self, keyword: str) -> pd.DataFrame:
        """Recherche par mot-clé dans titre/description"""
        try:
            conn = self._get_connection()
            query = """
                SELECT * FROM articles
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY published_at DESC
            """
            term = f"%{keyword}%"
            df = pd.read_sql_query(query, conn, params=(term, term))
            conn.close()

            self.save_search(keyword, len(df))
            return df

        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            return pd.DataFrame()

    # Search history

    def save_search(self, query: str, results_count: int):
        """Sauvegarde une recherche dans l'historique"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO search_history (query, results_count)
                VALUES (?, ?)
                """,
                (query, results_count),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Error saving search history: {e}")

    def get_search_history(self, limit: int = 10) -> pd.DataFrame:
        """Récupère l'historique des recherches"""
        try:
            conn = self._get_connection()
            query = f"SELECT * FROM search_history ORDER BY timestamp DESC LIMIT {limit}"
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            logger.error(f"Error retrieving search history: {e}")
            return pd.DataFrame()

    # Statistics

    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques sur la base de données"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            stats: Dict[str, Any] = {}

            cursor.execute("SELECT COUNT(*) FROM articles")
            stats["total_articles"] = cursor.fetchone()[0]

            cursor.execute("SELECT source, COUNT(*) FROM articles GROUP BY source")
            stats["by_source"] = dict(cursor.fetchall())

            cursor.execute("SELECT category, COUNT(*) FROM articles GROUP BY category")
            stats["by_category"] = dict(cursor.fetchall())

            cursor.execute("SELECT MAX(published_at) FROM articles")
            stats["latest_article_date"] = cursor.fetchone()[0]

            conn.close()
            return stats

        except Exception as e:
            logger.error(f"Error retrieving statistics: {e}")
            return {}


if __name__ == "__main__":
    # Test the Database class
    db = Database("data/test_techtrends.db")

    sample_articles = [
        {
            "title": "Test Article 1",
            "url": "https://example.com/1",
            "source": "HackerNews",
            "author": "Test Author",
            "points": 100,
            "comments": 50,
        }
    ]

    inserted = db.insert_articles(sample_articles)
    print(f"\n Inserted {inserted} articles")

    df = db.get_all_articles(limit=5)
    print(f"\n Retrieved {len(df)} articles")
    print(df[["title", "source"]])

    stats = db.get_statistics()
    print(f"\n Stats: {stats}")
