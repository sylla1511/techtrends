"""

BeautifulSoup is limited, particularly when dealing with JavaScript and when changing pages,
whereas Selenium allows you to generate an interface 
and go beyond traditional scraping when it is insufficient.
"""
from typing import List, Dict
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Example: Retrieving Hacker News headlines with Selenium
def get_hn_titles_with_selenium(max_articles: int = 10) -> List[Dict[str, str]]:
    """
    Exemple: récupérer quelques titres Hacker News avec Selenium.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # To be adapted according to your browser (Chrome, Chromium, etc.)
    driver = webdriver.Chrome(options=options)

    driver.get("https://news.ycombinator.com/")
    elements = driver.find_elements(By.CSS_SELECTOR, "span.titleline a")[:max_articles]

    results: List[Dict[str, str]] = []
    for el in elements:
        try:
            title = el.text
            url = el.get_attribute("href")
            results.append({"title": title, "url": url, "source": "HackerNews-Selenium"})
        except Exception as e:
            logger.warning(f"Error reading element: {e}")
            continue

    driver.quit()
    logger.info(f"Selenium fetched {len(results)} HN titles")
    return results


if __name__ == "__main__":
    arts = get_hn_titles_with_selenium(5)
    for a in arts:
        print(a["title"], "->", a["url"])
