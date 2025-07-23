# SentimentLens/backend/database.py

import sqlite3
from contextlib import contextmanager

DATABASE_URL = "sentiment_lens.db"

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def initialize_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Table for user-selected tickers
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL
            )
        ''')

        # Table for news articles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker_id INTEGER,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                source TEXT,
                published_at TIMESTAMP,
                content TEXT,
                FOREIGN KEY (ticker_id) REFERENCES tickers (id)
            )
        ''')

        # Table for sentiment analysis results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER,
                sentiment TEXT NOT NULL,
                confidence REAL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES articles (id)
            )
        ''')
        conn.commit()
        print("Database initialized successfully.")

if __name__ == '__main__':
    initialize_db()
