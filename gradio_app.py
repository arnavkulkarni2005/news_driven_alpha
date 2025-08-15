import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import requests
import os
from ml.predict import SentimentPredictor
from dotenv import load_dotenv
from datetime import datetime, timedelta

# --- Configuration & Initialization ---
load_dotenv()

# Load the sentiment prediction model
try:
    predictor = SentimentPredictor()
    model_loaded = True
    print("Sentiment model loaded successfully.")
except Exception as e:
    print(f"CRITICAL: Could not load sentiment model. Error: {e}")
    predictor = None
    model_loaded = False

# --- Data Fetching and Processing ---

def get_news_and_sentiment(ticker_symbol, days_back=30):
    """
    Fetches news from NewsAPI, analyzes sentiment, and returns a DataFrame.
    This function is self-contained for easy deployment on Hugging Face Spaces.
    """
    if not model_loaded:
        return pd.DataFrame()

    news_api_key = os.getenv("NEWS_API_KEY")
    if not news_api_key:
        print("Warning: NEWS_API_KEY not found. News fetching will fail.")
        return pd.DataFrame()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    url = (f"https://newsapi.org/v2/everything?"
           f"q={ticker_symbol}&"
           f"from={start_date.strftime('%Y-%m-%d')}&"
           f"to={end_date.strftime('%Y-%m-%d')}&"
           f"language=en&"
           f"sortBy=publishedAt&"
           f"apiKey={news_api_key}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get('articles', [])
        
        processed_articles = []
        for article in articles:
            text_to_analyze = article.get('content') or article.get('title') or ""
            if text_to_analyze:
                prediction = predictor.predict(text_to_analyze)
                processed_articles.append({
                    'published_at': article['publishedAt'],
                    'title': article['title'],
                    'sentiment': prediction['sentiment'],
                    'confidence': prediction['confidence'],
                    'url': article['url']
                })
        
        df = pd.DataFrame(processed_articles)
        if not df.empty:
            df['published_at'] = pd.to_datetime(df['published_at'])
        return df

    except requests.RequestException as e:
        print(f"Error fetching news from NewsAPI: {e}")
        return pd.DataFrame()

def get_stock_data(ticker_symbol, days_back=30):
    """Fetches historical stock data from Yahoo Finance."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    try:
        stock = yf.Ticker(ticker_symbol)
        hist = stock.history(start=start_date, end=end_date)
        return hist
    except Exception as e:
        print(f"Error fetching stock data for {ticker_symbol} from yfinance: {e}")
        return pd.DataFrame()

# --- Visualization & Interactivity Functions ---

def create_sentiment_dashboard(ticker_symbol, days_back=30):
    """
    Generates all plots and data for the main dashboard tab.
    Also returns the full sentiment dataframe to be stored for interactivity.
    """
    # Fetch data
    sentiment_df = get_news_and_sentiment(ticker_symbol, days_back)
    stock_df = get_stock_data(ticker_symbol, days_back)

    if sentiment_df.empty:
        # Return empty state if no data is found
        return None, None, None, pd.DataFrame(columns=["Date", "Title", "Sentiment", "Confidence", "Link"]), pd.DataFrame()

    # --- Chart 1: Sentiment vs. Stock Price ---
    sentiment_df['date'] = sentiment_df['published_at'].dt.date
    sentiment_mapping = {'positive': 1, 'neutral': 0, 'negative': -1}
    sentiment_df['sentiment_score'] = sentiment_df['sentiment'].map(sentiment_mapping)
    
    daily_avg_sentiment = sentiment_df.groupby('date')['sentiment_score'].mean().reset_index()
    daily_avg_sentiment['date'] = pd.to_datetime(daily_avg_sentiment['date'])

    fig_price_sentiment = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add Stock Price Trace
    fig_price_sentiment.add_trace(
        go.Scatter(x=stock_df.index, y=stock_df['Close'], name='Stock Price', line=dict(color='royalblue')),
        secondary_y=False,
    )
    # Add Sentiment Score Trace
    fig_price_sentiment.add_trace(
        go.Bar(x=daily_avg_sentiment['date'], y=daily_avg_sentiment['sentiment_score'], name='Avg. Sentiment Score', marker_color='lightcoral', opacity=0.6),
        secondary_y=True,
    )
    fig_price_sentiment.update_layout(
        title_text=f'<b>Stock Price vs. Average Daily Sentiment for ${ticker_symbol}</b>',
        xaxis_title='Date',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    fig_price_sentiment.update_yaxes(title_text="<b>Stock Price (USD)</b>", secondary_y=False)
    fig_price_sentiment.update_yaxes(title_text="<b>Average Sentiment Score</b>", secondary_y=True)


    # --- Chart 2: Daily Sentiment Breakdown ---
    daily_counts = sentiment_df.groupby([sentiment_df['published_at'].dt.date, 'sentiment']).size().unstack(fill_value=0)
    fig_daily_breakdown = go.Figure()
    colors = {'positive': 'green', 'negative': 'red', 'neutral': 'grey'}
    for sentiment in ['positive', 'negative', 'neutral']:
        if sentiment in daily_counts.columns:
            fig_daily_breakdown.add_trace(go.Bar(
                x=daily_counts.index,
                y=daily_counts[sentiment],
                name=sentiment.capitalize(),
                marker_color=colors[sentiment]
            ))
    fig_daily_breakdown.update_layout(
        barmode='stack',
        title_text=f'<b>Daily News Sentiment Breakdown for ${ticker_symbol}</b>',
        xaxis_title='Date',
        yaxis_title='Number of Articles',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # --- Chart 3: Overall Sentiment Distribution ---
    sentiment_dist = sentiment_df['sentiment'].value_counts()
    fig_pie = go.Figure(data=[go.Pie(
        labels=sentiment_dist.index, 
        values=sentiment_dist.values,
        hole=.3,
        marker_colors=[colors[s] for s in sentiment_dist.index]
    )])
    fig_pie.update_layout(
        title_text=f'<b>Overall Sentiment Distribution for ${ticker_symbol}</b>'
    )
    
    # --- Table: Recent News ---
    news_table_df = sentiment_df[['published_at', 'title', 'sentiment', 'confidence', 'url']].copy()
    news_table_df.rename(columns={
        'published_at': 'Date', 'title': 'Title', 'sentiment': 'Sentiment', 
        'confidence': 'Confidence', 'url': 'Link'
    }, inplace=True)
    news_table_df['Date'] = news_table_df['Date'].dt.strftime('%Y-%m-%d %H:%M')
    news_table_df['Confidence'] = news_table_df['Confidence'].round(2)

    # Return all plots, the initial news table, and the full dataframe for state
    return fig_price_sentiment, fig_daily_breakdown, fig_pie, news_table_df.head(20), sentiment_df

def filter_news_by_date(evt: gr.SelectData, full_df: pd.DataFrame):
    """
    Callback function to filter the news DataFrame when a user clicks on a plot.
    """
    if full_df is None or full_df.empty:
        return pd.DataFrame(columns=["Date", "Title", "Sentiment", "Confidence", "Link"])
    
    # The x-value of the selected bar is the date string
    selected_date_str = evt.value
    selected_date = pd.to_datetime(selected_date_str).date()
    
    # Filter the full dataframe based on the clicked date
    filtered_df = full_df[full_df['published_at'].dt.date == selected_date]
    
    # Format the filtered dataframe for display
    news_table_df = filtered_df[['published_at', 'title', 'sentiment', 'confidence', 'url']].copy()
    news_table_df.rename(columns={
        'published_at': 'Date', 'title': 'Title', 'sentiment': 'Sentiment', 
        'confidence': 'Confidence', 'url': 'Link'
    }, inplace=True)
    news_table_df['Date'] = news_table_df['Date'].dt.strftime('%Y-%m-%d %H:%M')
    news_table_df['Confidence'] = news_table_df['Confidence'].round(2)
    
    return news_table_df


# --- Gradio UI Definition ---

with gr.Blocks(theme=gr.themes.Soft(), title="SentimentLens") as demo:
    gr.Markdown("# 📊 SentimentLens: Financial News Analysis Dashboard")
    
    # State component to hold the full dataframe for interactive filtering
    full_sentiment_data = gr.State()
    
    with gr.Tabs():
        # --- Main Dashboard Tab ---
        with gr.TabItem("Sentiment Dashboard"):
            with gr.Row():
                ticker_input = gr.Textbox(label="Enter Stock Ticker", placeholder="e.g., AAPL, GOOGL, TSLA...", value="AAPL")
                days_input = gr.Slider(minimum=7, maximum=90, value=30, step=1, label="Days of History")
                analyze_button = gr.Button("Analyze", variant="primary")

            with gr.Row():
                pie_chart = gr.Plot()
            
            with gr.Row():
                price_sentiment_plot = gr.Plot()

            with gr.Row():
                daily_breakdown_plot = gr.Plot()
            
            with gr.Row():
                gr.Markdown("### Recent News Articles\n*(Click on a bar in the 'Daily News Sentiment' chart above to filter articles for that day)*")
                news_output = gr.DataFrame(headers=["Date", "Title", "Sentiment", "Confidence", "Link"], interactive=False, wrap=True)

        # --- Live Analysis Tab ---
        with gr.TabItem("Live Sentiment Analysis"):
            gr.Markdown("### Test the FinBERT Model in Real-Time")
            with gr.Row():
                live_text_input = gr.Textbox(lines=7, label="Enter Financial Text", placeholder="e.g., 'The company's earnings exceeded all expectations this quarter.'")
            with gr.Row():
                live_analyze_button = gr.Button("Predict Sentiment", variant="primary")
            with gr.Row():
                live_output = gr.Label(label="Analysis Result")

        # --- About Tab ---
        with gr.TabItem("About"):
            gr.Markdown(
                """
                ## About SentimentLens
                SentimentLens is a comprehensive web application designed to analyze the sentiment of financial news articles for user-specified stock tickers. It provides real-time insights into market mood by fetching the latest news, processing it through a sophisticated FinBERT model, and visualizing the sentiment trends on an interactive dashboard.

                ### Technology
                - **UI**: Gradio & Plotly
                - **Machine Learning**: Hugging Face Transformers, PyTorch, FinBERT
                - **Data Sources**: NewsAPI for news, Yahoo Finance for stock prices.
                
                This application is deployed on **Hugging Face Spaces**.
                """
            )

    # --- Event Handlers ---
    analyze_button.click(
        fn=create_sentiment_dashboard,
        inputs=[ticker_input, days_input],
        outputs=[price_sentiment_plot, daily_breakdown_plot, pie_chart, news_output, full_sentiment_data]
    )
    
    live_analyze_button.click(
        fn=predictor.predict if model_loaded else lambda x: {"Error": "Model not loaded"},
        inputs=live_text_input,
        outputs=live_output
    )
    
    # NEW: Event handler for making the plot interactive
    daily_breakdown_plot.select(
        fn=filter_news_by_date,
        inputs=[full_sentiment_data],
        outputs=[news_output]
    )


# --- Launch the App ---
if __name__ == "__main__":
    demo.launch()
