# SentimentLens/app.py

import streamlit as st
import plotly.express as px
import pandas as pd
from backend.database import get_db_connection

# --- Page Configuration ---
st.set_page_config(
    page_title="SentimentLens Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- Helper Functions ---
def get_tickers():
    with get_db_connection() as conn:
        return pd.read_sql_query("SELECT symbol FROM tickers", conn)

def add_ticker(symbol):
    with get_db_connection() as conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tickers (symbol) VALUES (%s)", (symbol.upper(),))
            conn.commit()
            st.success(f"Added ticker: {symbol.upper()}")
        except conn.IntegrityError:
            st.warning(f"Ticker {symbol.upper()} is already tracked.")
        finally:
            cursor.close()


def get_sentiment_data(ticker_symbol):
    query = """
        SELECT
            a.published_at,
            s.sentiment,
            s.confidence,
            a.title,
            a.url
        FROM sentiment_data s
        JOIN articles a ON s.article_id = a.id
        JOIN tickers t ON a.ticker_id = t.id
        WHERE t.symbol = %s
        ORDER BY a.published_at DESC
    """
    with get_db_connection() as conn:
        # The params argument for read_sql_query with psycopg2 needs a list or tuple
        return pd.read_sql_query(query, conn, params=(ticker_symbol,))

# --- UI Components ---
st.title("📊 SentimentLens: Financial News Sentiment Engine")

# --- Sidebar for Ticker Management ---
st.sidebar.header("Manage Tickers")
with st.sidebar.form("add_ticker_form"):
    new_ticker = st.text_input("Add a new stock ticker (e.g., AAPL, GOOGL)")
    add_button = st.form_submit_button("Add Ticker")
    if add_button and new_ticker:
        add_ticker(new_ticker)

st.sidebar.header("Tracked Tickers")
tracked_tickers = get_tickers()
selected_ticker = st.sidebar.selectbox(
    "Select a ticker to view sentiment",
    tracked_tickers['symbol'].tolist()
)

# --- Main Dashboard ---
if selected_ticker:
    st.header(f"Sentiment Analysis for ${selected_ticker}")
    sentiment_df = get_sentiment_data(selected_ticker)

    if not sentiment_df.empty:
        # --- Sentiment Over Time Chart ---
        st.subheader("Sentiment Trend")
        sentiment_df['published_at'] = pd.to_datetime(sentiment_df['published_at'])
        sentiment_counts = sentiment_df.set_index('published_at').resample('D')['sentiment'].value_counts().unstack(fill_value=0)
        fig = px.bar(sentiment_counts, x=sentiment_counts.index, y=sentiment_counts.columns,
                     title=f"Daily Sentiment Count for ${selected_ticker}",
                     labels={'value': 'Number of Articles', 'published_at': 'Date'},
                     color_discrete_map={'positive': 'green', 'negative': 'red', 'neutral': 'grey'})
        st.plotly_chart(fig, use_container_width=True)

        # --- Latest News Articles ---
        st.subheader("Recent News and Sentiment")
        for _, row in sentiment_df.head(10).iterrows():
            st.markdown(f"**[{row['title']}]({row['url']})**")
            color = "green" if row['sentiment'] == 'positive' else "red" if row['sentiment'] == 'negative' else "grey"
            st.markdown(f"> Sentiment: <span style='color:{color};'>{row['sentiment']}</span> (Confidence: {row['confidence']:.2f})", unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.info(f"No sentiment data available for ${selected_ticker}. The backend might still be processing.")
else:
    st.info("Add and select a ticker from the sidebar to begin.")
