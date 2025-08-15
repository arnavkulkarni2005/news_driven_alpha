from flask import Flask, jsonify
import pandas as pd
from backend.database import get_db_connection
import threading
import time
import schedule
from scripts.scheduled_tasks import run_all_tasks

app = Flask(__name__)

def get_sentiment_data_for_api(ticker_symbol):
    """Helper function to fetch sentiment data for the API."""
    query = """
        SELECT
            a.published_at,
            s.sentiment,
            s.confidence,
            a.title,
            a.url,
            t.symbol
        FROM sentiment_data s
        JOIN articles a ON s.article_id = a.id
        JOIN tickers t ON a.ticker_id = t.id
        WHERE t.symbol = %s
        ORDER BY a.published_at DESC
    """
    with get_db_connection() as conn:
        df = pd.read_sql_query(query, conn, params=(ticker_symbol,))
        return df.to_dict(orient='records')

@app.route('/api/tickers', methods=['GET'])
def get_tickers_api():
    """API endpoint to get the list of all tracked tickers."""
    with get_db_connection() as conn:
        tickers_df = pd.read_sql_query("SELECT symbol FROM tickers", conn)
    return jsonify(tickers_df['symbol'].tolist())

@app.route('/api/sentiment/<string:ticker_symbol>', methods=['GET'])
def get_sentiment_api(ticker_symbol):
    """API endpoint to get sentiment data for a specific ticker."""
    data = get_sentiment_data_for_api(ticker_symbol.upper())
    if data:
        return jsonify(data)
    else:
        return jsonify({"error": f"No data found for ticker {ticker_symbol}"}), 404

def run_scheduler():
    """Runs the scheduled tasks in a loop."""
    # Run the tasks once immediately on startup
    run_all_tasks() 
    
    # Then schedule them to run every hour
    schedule.every().hour.do(run_all_tasks)
    while True:
        schedule.run_pending()
        time.sleep(1)

# This block will not run when using Gunicorn, but it's good for local testing.
# The entrypoint.sh script will start Gunicorn directly.
if __name__ == '__main__':
    # Start the scheduler in a background thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Run the Flask app
    app.run(debug=True, port=5000)

# Start the scheduler when the app is run with Gunicorn
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()
