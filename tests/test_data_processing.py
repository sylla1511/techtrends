import pandas as pd

from src.data_processing import DataProcessor

# Test cases for DataProcessor
def test_articles_to_dataframe_basic():
    processor = DataProcessor()
    articles = [
        {"title": "Test 1", "points": 10, "source": "HackerNews"},
        {"title": "Test 2", "points": 20, "source": "Dev.to"},
    ]

    df = processor.articles_to_dataframe(articles)

    assert len(df) == 2
    assert "title" in df.columns
    assert "points" in df.columns
    assert df["points"].sum() == 30
    assert set(df["source"]) == {"HackerNews", "Dev.to"}

# Additional test cases 1
def test_categorize_by_keywords():
    processor = DataProcessor()
    df = pd.DataFrame(
        [
            {"title": "Python for Data Science"},
            {"title": "Docker for DevOps"},
            {"title": "Random title"},
        ]
    )

    keywords = {
        "Python": ["python"],
        "DevOps": ["docker"],
    }

    df_cat = processor.categorize_by_keywords(df, keywords)

    assert "category" in df_cat.columns
    cats = df_cat["category"].tolist()
    assert "Python" in cats
    assert "DevOps" in cats
    assert "Other" in cats

# Additional test cases 2
def test_get_trending_topics():
    processor = DataProcessor()
    df = pd.DataFrame(
        [
            {"title": "Python machine learning tutorial"},
            {"title": "Advanced Python tips"},
            {"title": "Docker and DevOps"},
        ]
    )

    topics = processor.get_trending_topics(df, column="title", top_n=5)

    assert isinstance(topics, list)
    assert len(topics) > 0
    word, count = topics[0]
    assert isinstance(word, str)
    assert isinstance(count, int)
