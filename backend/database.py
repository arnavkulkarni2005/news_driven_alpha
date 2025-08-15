import os
import psycopg2
from contextlib import contextmanager

# The DATABASE_URL will be provided by Render's environment
DATABASE_URL = os.environ.get('DATABASE_URL')

@contextmanager
def get_db_connection():
    """Context manager for PostgreSQL database connections."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def initialize_db():
    """Initializes the database with the required tables."""
    # Important: SQL syntax for auto-incrementing keys is different
    # and we need to adapt placeholders from '?' to '%s'.
    
    tickers_table = """
        CREATE TABLE IF NOT EXISTS tickers (
            id SERIAL PRIMARY KEY,
            symbol TEXT UNIQUE NOT NULL
        );
    """
    
    articles_table = """
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            ticker_id INTEGER,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            source TEXT,
            published_at TIMESTAMP,
            content TEXT,
            FOREIGN KEY (ticker_id) REFERENCES tickers (id)
        );
    """
    
    sentiment_data_table = """
        CREATE TABLE IF NOT EXISTS sentiment_data (
            id SERIAL PRIMARY KEY,
            article_id INTEGER,
            sentiment TEXT NOT NULL,
            confidence REAL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES articles (id)
        );
    """

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(tickers_table)
        cursor.execute(articles_table)
        cursor.execute(sentiment_data_table)
        conn.commit()
        print("Database initialized successfully.")

if __name__ == '__main__':
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set.")
    initialize_db()