# SentimentLens/ml/preprocess.py

import re

class RuleBasedFilter:
    def __init__(self):
        # Keywords that often indicate non-actionable news
        self.noise_keywords = [
            'quarterly report', 'earnings call', 'insider transaction',
            'analyst rating', 'dividend', 'stock split', 'rumor',
            'market update', 'daily brief'
        ]

    def is_noisy(self, headline: str) -> bool:
        headline_lower = headline.lower()
        for keyword in self.noise_keywords:
            if keyword in headline_lower:
                return True
        return False

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'http\S+', '', text) # Remove URLs
    text = re.sub(r'[^a-zA-Z\s]', '', text) # Remove non-alphabetic characters
    text = re.sub(r'\s+', ' ', text).strip() # Remove extra whitespace
    return text
