# SentimentLens/scripts/data_collector.py

import requests
from backend.config import Config
from backend.database import get_db_connection

class NewsFetcher:
    def __init__(self):
        self.api_key = Config.NEWS_API_KEY
        if not self.api_key:
            raise ValueError("NEWS_API_KEY is not set.")
        self.base_url = "https://newsapi.org/v2/everything"

    def fetch_and_store_news(self):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, symbol FROM tickers")
            tickers = cursor.fetchall()

            for ticker in tickers:
                print(f"Fetching news for {ticker['symbol']}...")
                params = {
                    'q': ticker['symbol'],
                    'apiKey': self.api_key,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 20 # Fetch recent 20 articles
                }
                try:
                    response = requests.get(self.base_url, params=params)
                    response.raise_for_status()
                    articles = response.json().get('articles', [])

                    for article in articles:
                        # Avoid duplicates
                        cursor.execute("SELECT id FROM articles WHERE url = ?", (article['url'],))
                        if cursor.fetchone():
                            continue

                        cursor.execute(
                            """
                            INSERT INTO articles (ticker_id, title, url, source, published_at, content)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                ticker['id'],
                                article['title'],
                                article['url'],
                                article.get('source', {}).get('name'),
                                article['publishedAt'],
                                article.get('content') or article.get('description')
                            )
                        )
                    conn.commit()
                    print(f"Stored {len(articles)} new articles for {ticker['symbol']}.")
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching news for {ticker['symbol']}: {e}")

if __name__ == '__main__':
    fetcher = NewsFetcher()
    fetcher.fetch_and_store_news()
