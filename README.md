# 📊 SentimentLens: Financial News Sentiment Analysis Engine

SentimentLens is a comprehensive web application designed to analyze the sentiment of financial news articles for user-specified stock tickers. It provides real-time insights into market mood by fetching the latest news, processing it through a sophisticated FinBERT model, and visualizing the sentiment trends on an interactive dashboard.

This project is built with a modern, scalable architecture, containerized with Docker, and ready for cloud deployment, making it an excellent showcase of full-stack development and MLOps principles.

## 💡 Why SentimentLens Matters in Today's Market

In an era of unprecedented market volatility and information overload, retail and institutional investors alike face the challenge of sifting through a constant barrage of news. Financial markets react in seconds to headlines, press releases, and global events. SentimentLens is designed to tackle this challenge head-on:

* **Tackling Information Overload**: It's impossible for a human to read and emotionally process every piece of news about their investments. SentimentLens automates this process, distilling thousands of articles into a clear, actionable signal: the prevailing market mood.
* **Gaining a Competitive Edge**: Professional trading firms have used automated sentiment analysis for years to gain an edge. This project democratizes that technology, providing retail investors with a powerful tool to understand the narrative driving a stock's price.
* **Making Data-Driven Decisions**: Gut feelings are no longer enough. By quantifying sentiment, investors can add a crucial data point to their analysis, helping them make more informed, less emotional decisions about when to buy, hold, or sell.
* **Proactive Risk Management**: A sudden surge in negative news can be a leading indicator of potential trouble. SentimentLens acts as an early warning system, alerting users to shifts in market perception so they can investigate potential risks before they impact their portfolio.

Ultimately, SentimentLens helps cut through the noise, providing a clear and quantitative measure of market sentiment to navigate today's complex financial landscape.

## ✨ Features

* **Dynamic Ticker Management**: Users can add and track any stock ticker (e.g., AAPL, GOOGL, TSLA).
* **Automated News Aggregation**: A background scheduler automatically fetches the latest financial news from the [NewsAPI](https://newsapi.org/) for all tracked tickers.
* **Advanced Sentiment Analysis**: Utilizes a fine-tuned **FinBERT model** (based on Google's BERT) specifically trained on financial text to classify articles as positive, negative, or neutral.
* **Interactive Dashboard**: The frontend, built with **Streamlit**, provides a clean and intuitive user interface to visualize data.
* **Sentiment Trend Visualization**: A dynamic bar chart displays the daily count of positive, negative, and neutral articles, allowing users to spot trends over time.
* **Detailed News Feed**: Displays a list of the most recent articles with their titles, a direct link to the source, and the corresponding sentiment score and confidence level.
* **RESTful API**: A **Flask**-based backend serves the processed data to the frontend, allowing for a decoupled and scalable architecture.

## 🛠️ Tech Stack & Architecture

This project uses a multi-service architecture, with each component containerized using Docker.

* **Frontend**: **Streamlit** (for the interactive dashboard)
* **Backend**: **Flask** & **Gunicorn** (for the REST API)
* **Machine Learning**: **Hugging Face Transformers**, **PyTorch**, **FinBERT**
* **Database**: **PostgreSQL** (for storing articles, tickers, and sentiment data)
* **Data Processing**: **Pandas**
* **Scheduling**: **schedule** library
* **Containerization**: **Docker** & **Docker Compose**
* **Deployment**: **Render** (configured via `render.yaml`)

#### System Flow

1.  **Scheduler**: Periodically fetches news for tickers stored in the PostgreSQL database via the NewsAPI.
2.  **ML Model**: The scheduler feeds new articles to the FinBERT model, which analyzes the sentiment.
3.  **Database**: The results (sentiment and confidence) are stored back in the PostgreSQL database.
4.  **Backend API**: The Flask API queries the database to get sentiment data for a specific ticker.
5.  **Frontend**: The Streamlit dashboard calls the Flask API and visualizes the data for the user.

## 🚀 Local Setup and Installation

Follow these steps to run the project on your local machine.

### Prerequisites

* Python 3.9+
* Docker and Docker Compose
* A NewsAPI key (get one for free at [newsapi.org](https://newsapi.org/))

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <your-project-directory>
```

### 2. Set Up Environment Variables

Create a `.env` file in the root of the project and add your NewsAPI key:

```
NEWS_API_KEY="YOUR_NEWS_API_KEY_HERE"
```

### 3. Initialize the Database

The project uses a local SQLite database for development. Run the following command to create the `sentiment_lens.db` file and set up the necessary tables:

```bash
python -m backend.database
```

### 4. Build and Run with Docker Compose

This is the easiest way to run all services (frontend, backend, and scheduler) at once.

```bash
docker-compose up --build
```

* The **Streamlit frontend** will be available at `http://localhost:8501`.
* The **Flask API** will be running at `http://localhost:5000`.

## ☁️ Deployment

This project is configured for seamless deployment on **Render** using the `render.yaml` file.

1.  **Push to GitHub**: Ensure all your code is pushed to a GitHub repository.
2.  **Create a New Blueprint**: On the Render dashboard, create a new "Blueprint" and select your repository.
3.  **Configuration**: Render will automatically detect the `render.yaml` file and configure the services:
    * A **PostgreSQL** database instance.
    * A **web service** for the Flask API and scheduler.
    * A **web service** for the Streamlit frontend.
4.  **Add Environment Variable**: When prompted, add your `NEWS_API_KEY` as a secret environment variable.
5.  **Deploy**: Click "Apply" to build and deploy the application. Render will provide a public URL for the Streamlit frontend.

## 🔮 Future Enhancements

* **Advanced Visualizations**: Implement candlestick charts to correlate sentiment with stock price movements.
* **Named Entity Recognition (NER)**: Extract and display key entities (companies, people, products) mentioned in articles.
* **Broader Data Sources**: Integrate other news sources like Alpaca or financial forums like Reddit.
* **User Authentication**: Allow users to create accounts and save their personalized list of tickers.
