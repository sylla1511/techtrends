"""
This module uses the dev.t API to retrieve articles, processes them, 
and provides methods for retrieving 
the latest articles, most popular articles, or articles filtered by tag. 
"""
import requests
from typing import List, Dict, Any
import logging
from datetime import datetime
import sys
from pathlib import Path

# Adding the project root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
    
from config import MAX_ARTICLES_PER_SOURCE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dev.to API client
class DevToAPI:
    """Client API pour Dev.to"""

    def __init__(self, max_articles: int = MAX_ARTICLES_PER_SOURCE):
        """
        Args:
            max_articles: Nombre maximum d'articles à récupérer
        """
        self.base_url = "https://dev.to/api/articles"
        self.max_articles = max_articles
        self.headers = {
            "User-Agent": "TechTrends/1.0"
        }
# Internal method for making API requests
    def _fetch(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            resp = requests.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=10,
            )
            resp.raise_for_status()
            raw_articles = resp.json()
            articles: List[Dict[str, Any]] = []

            for art in raw_articles:
                processed = {
                    "title": art.get("title", ""),
                    "description": art.get("description", ""),
                    "url": art.get("url", ""),
                    "published_at": art.get("published_at", ""),
                    "tags": art.get("tag_list", []),
                    "reactions": art.get("positive_reactions_count", 0),
                    "comments": art.get("comments_count", 0),
                    "reading_time": art.get("reading_time_minutes", 0),
                    "author": art.get("user", {}).get("name", "Unknown"),
                    "source": "Dev.to",
                    "fetched_at": datetime.now().isoformat(),
                }
                articles.append(processed)

            logger.info(f"Fetched {len(articles)} articles from Dev.to")
            return articles

        except Exception as e:
            logger.error(f"Error fetching Dev.to articles: {e}")
            return []
# Public methods to get articles
    def get_latest_articles(self, per_page: int = 30, page: int = 1) -> List[Dict[str, Any]]:
        """
        Derniers articles (état 'fresh')
        """
        per_page = min(per_page, self.max_articles)
        params = {
            "per_page": per_page,
            "page": page,
            "state": "fresh",
        }
        logger.info("Fetching latest articles from Dev.to...")
        return self._fetch(params)

    def get_articles_by_tag(self, tag: str, per_page: int = 30) -> List[Dict[str, Any]]:
        """
        Articles filtrés par tag (ex: 'python')
        """
        per_page = min(per_page, self.max_articles)
        params = {
            "per_page": per_page,
            "tag": tag,
        }
        logger.info(f"Fetching Dev.to articles with tag='{tag}'...")
        return self._fetch(params)

    def get_top_articles(self, per_page: int = 30) -> List[Dict[str, Any]]:
        """
        Articles populaires des 15 derniers jours
        """
        per_page = min(per_page, self.max_articles)
        params = {
            "per_page": per_page,
            "top": 15,
        }
        logger.info("Fetching top Dev.to articles...")
        return self._fetch(params)

# Example
if __name__ == "__main__":
    api = DevToAPI(max_articles=10)

    print("\n Top articles Dev.to:")
    top_articles = api.get_top_articles(per_page=5)
    for idx, art in enumerate(top_articles[:3], 1):
        print(f"{idx}. {art['title']} ({art['reactions']}❤️, {art['comments']}💬) -> {art['url']}")
