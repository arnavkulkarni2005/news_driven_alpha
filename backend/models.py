
from pydantic import BaseModel
from typing import List, Optional

class Ticker(BaseModel):
    id: Optional[int] = None
    symbol: str

class Article(BaseModel):
    id: Optional[int] = None
    ticker_id: int
    title: str
    url: str
    source: Optional[str] = None
    published_at: str
    content: Optional[str] = None

class Sentiment(BaseModel):
    id: Optional[int] = None
    article_id: int
    sentiment: str
    confidence: float
