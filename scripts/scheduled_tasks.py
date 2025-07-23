
import time
import schedule
import pandas as pd
from datetime import datetime, timedelta

from .data_collector import NewsFetcher
from .alerter import Alerter

# These are top-level imports and are correct
from ml.predict import SentimentPredictor
from ml.preprocess import RuleBasedFilter
from backend.database import get_db_connection


def process_new_articles():
    print("Running job: Processing new articles for sentiment...")
    predictor = SentimentPredictor()
    rb_filter = RuleBasedFilter()
    
    query = """
        SELECT a.id, a.title, a.content
        FROM articles a
        LEFT JOIN sentiment_data s ON a.id = s.article_id
        WHERE s.id IS NULL
    """
    with get_db_connection() as conn:
        articles_to_process = pd.read_sql_query(query, conn)
        
        if articles_to_process.empty:
            print("No new articles to process.")
            return

        print(f"Found {len(articles_to_process)} new articles to process.")
        
        for _, article in articles_to_process.iterrows():
            # Rule-based filtering
            if rb_filter.is_noisy(article['title']):
                print(f"Skipping noisy headline: {article['title']}")
                continue

            # Predict sentiment
            text_to_analyze = article['content'] or article['title']
            prediction = predictor.predict(text_to_analyze)

            # Store sentiment
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO sentiment_data (article_id, sentiment, confidence)
                VALUES (?, ?, ?)
                """,
                (article['id'], prediction['sentiment'], prediction['confidence'])
            )
        conn.commit()
    print("Article processing job complete.")


def check_for_alerts():
    print("Running job: Checking for alert conditions...")
    alerter = Alerter()
    
    # Alert if a ticker has > 3 negative articles in the last 24 hours
    alert_threshold = 3
    time_window = datetime.now() - timedelta(hours=24)
    
    query = """
        SELECT
            t.symbol,
            COUNT(s.id) as negative_count
        FROM sentiment_data s
        JOIN articles a ON s.article_id = a.id
        JOIN tickers t ON a.ticker_id = t.id
        WHERE
            s.sentiment = 'negative' AND
            a.published_at >= ?
        GROUP BY t.symbol
        HAVING COUNT(s.id) >= ?
    """
    
    with get_db_connection() as conn:
        alerts_needed = pd.read_sql_query(query, conn, params=(time_window.isoformat(), alert_threshold))
        
        for _, row in alerts_needed.iterrows():
            subject = f"Sentiment Alert for {row['symbol']}"
            body = (
                f"SentimentLens has detected {row['negative_count']} negative articles "
                f"for {row['symbol']} in the last 24 hours. "
                "You may want to review this ticker."
            )
            alerter.send_alert(subject, body)
            
    print("Alert check complete.")


def run_all_tasks():
    print("\n--- Running Full ETL and Alerting Cycle ---")
    # 1. Fetch new data
    fetcher = NewsFetcher()
    fetcher.fetch_and_store_news()
    
    # 2. Process fetched data
    process_new_articles()
    
    # 3. Check for alerts
    check_for_alerts()
    print("--- Cycle Complete ---")


def main():
    schedule.every().hour.do(run_all_tasks)

    print("Scheduler started. First run will be in an hour.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    print("--- Confirming execution of the correct 'scheduled_tasks.py' file. ---")
    run_all_tasks()
    main()
