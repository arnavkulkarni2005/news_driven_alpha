

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Holds all configuration for the application."""
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    DATABASE_URL = "sentiment_lens.db"
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = os.getenv("SMTP_PORT")
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    ALERT_RECIPIENT_EMAIL = os.getenv("ALERT_RECIPIENT_EMAIL")
