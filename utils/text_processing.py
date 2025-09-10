import re
from typing import List

class TextProcessor:
    """Utility class for text processing and cleaning"""
    
    def __init__(self):
        self.stop_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'madam', 'sir', 'hello', 'yes', 'no'}
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove punctuation except useful ones
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        return text.strip()
    
    def normalize_units(self, text: str) -> str:
        """Normalize unit representations"""
        # Standardize feet representations
        text = re.sub(r'\bft\b', 'feet', text, flags=re.IGNORECASE)
        text = re.sub(r'\bfoot\b', 'feet', text, flags=re.IGNORECASE)
        
        # Standardize tonne representations  
        text = re.sub(r'\bmt\b', 'tons', text, flags=re.IGNORECASE)
        text = re.sub(r'\btonne[s]?\b', 'tons', text, flags=re.IGNORECASE)
        
        return text