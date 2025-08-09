from transformers import pipeline
from collections import Counter
import re
from typing import Dict, List

class AIProcessor:
    def __init__(self):
        # Initialize Hugging Face models (these will download on first run)
        self.sentiment_analyzer = pipeline("sentiment-analysis", 
                                         model="cardiffnlp/twitter-roberta-base-sentiment-latest")
        
    async def update_provider_insights(self, provider_id: str):
        """Update AI insights for a provider based on their reviews."""
        # This would fetch reviews and process them
        # For now, placeholder implementation
        pass
    
    def extract_keywords(self, review_text: str) -> List[str]:
        """Extract key themes from review text."""
        # Simple keyword extraction
        keywords = {
            'punctual': ['time', 'punctual', 'late', 'early', 'schedule'],
            'skilled': ['skill', 'expert', 'professional', 'quality', 'experienced'],
            'polite': ['polite', 'rude', 'behavior', 'attitude', 'respectful'],
            'clean': ['clean', 'mess', 'tidy', 'organized'],
            'price': ['cheap', 'expensive', 'reasonable', 'cost', 'price', 'money']
        }
        
        found_themes = []
        text_lower = review_text.lower()
        
        for theme, words in keywords.items():
            if any(word in text_lower for word in words):
                found_themes.append(theme)
        
        return found_themes
