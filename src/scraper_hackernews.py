"""

We coded this to scrape the Hacker News site, 
so it automatically collects articles from the home page and metadata,
without forgetting to set a limit to avoid being blocked, and then returns the results.
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging
from datetime import datetime
import time
import sys
from pathlib import Path

# Adding the project root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parents[1] 
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import SCRAPING_DELAY, MAX_ARTICLES_PER_SOURCE


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hacker News Scraper class
class HackerNewsScraper:
    """Scraper pour récupérer les articles de Hacker News"""

    def __init__(self, max_articles: int = MAX_ARTICLES_PER_SOURCE, delay: float = SCRAPING_DELAY):
        """
        Args:
            max_articles: Nombre maximum d'articles à récupérer
            delay: Délai entre les requêtes en secondes
        """
        self.base_url = "https://news.ycombinator.com/"
        self.max_articles = max_articles
        self.delay = delay
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
# Method to scrape front page
    def scrape_frontpage(self) -> List[Dict[str, Any]]:
        """
        Scrape la page d'accueil de Hacker News

        Returns:
            Liste de dictionnaires contenant les articles
        """
        try:
            logger.info("Scraping Hacker News front page...")
            resp = requests.get(self.base_url, headers=self.headers, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            articles: List[Dict[str, Any]] = []

            storylinks = soup.find_all("span", class_="titleline")
            subtexts = soup.find_all("td", class_="subtext")

            for idx, (storylink, subtext) in enumerate(zip(storylinks, subtexts)):
                if idx >= self.max_articles:
                    break

                try:
                    link_tag = storylink.find("a")
                    if not link_tag:
                        continue

                    title = link_tag.get_text(strip=True)
                    url = link_tag.get("href", "")

                    if url.startswith("item?id="):
                        url = self.base_url + url

                    score_tag = subtext.find("span", class_="score")
                    points = 0
                    if score_tag:
                        txt = score_tag.get_text(strip=True)
                        points = int(txt.split()[0]) if txt else 0

                    comments = 0
                    comment_links = subtext.find_all("a")
                    if comment_links:
                        last = comment_links[-1].get_text(strip=True)
                        if "comment" in last:
                            first = last.split()[0]
                            comments = int(first) if first.isdigit() else 0

                    author_tag = subtext.find("a", class_="hnuser")
                    author = author_tag.get_text(strip=True) if author_tag else "Unknown"

                    article = {
                        "title": title,
                        "url": url,
                        "points": points,
                        "comments": comments,
                        "author": author,
                        "source": "HackerNews",
                        "scraped_at": datetime.now().isoformat(),
                        "description": "",
                        "reactions": 0,
                        "reading_time": 0,
                        "tags": [],
                    }
                    articles.append(article)

                except Exception as e:
                    logger.warning(f"Error parsing article {idx}: {e}")
                    continue

            logger.info(f"Successfully scraped {len(articles)} articles from Hacker News")
            time.sleep(self.delay)
            return articles

        except Exception as e:
            logger.error(f"Error scraping Hacker News: {e}")
            return []


if __name__ == "__main__":
    scraper = HackerNewsScraper(max_articles=10)
    arts = scraper.scrape_frontpage()
    print(f"\n Scraped {len(arts)} articles")
    if arts:
        print("Premier:", arts[0]["title"], "->", arts[0]["url"])
