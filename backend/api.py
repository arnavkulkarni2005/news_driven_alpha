from flask import Flask, jsonify
import pandas as pd
from backend.database import get_db_connection

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
        # The params argument for read_sql_query with psycopg2 needs a list or tuple
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
