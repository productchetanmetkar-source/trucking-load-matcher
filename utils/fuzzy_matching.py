from fuzzywuzzy import fuzz, process
from typing import List, Tuple, Optional

class FuzzyMatcher:
    """Utility class for fuzzy string matching"""
    
    def __init__(self, threshold: int = 80):
        self.threshold = threshold
    
    def find_best_match(self, query: str, choices: List[str], 
                       scorer=fuzz.ratio) -> Optional[Tuple[str, int]]:
        """Find best match from choices with score"""
        result = process.extractOne(query, choices, scorer=scorer)
        if result and result[1] >= self.threshold:
            return result
        return None
    
    def find_all_matches(self, query: str, choices: List[str], 
                        limit: int = 3) -> List[Tuple[str, int]]:
        """Find all matches above threshold"""
        results = process.extract(query, choices, limit=limit)
        return [(match, score) for match, score in results if score >= self.threshold]