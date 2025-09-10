import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Matching thresholds
    MATCH_THRESHOLD_HIGH = float(os.getenv('MATCH_THRESHOLD_HIGH', 0.85))
    MATCH_THRESHOLD_MEDIUM = float(os.getenv('MATCH_THRESHOLD_MEDIUM', 0.60))
    MATCH_THRESHOLD_LOW = float(os.getenv('MATCH_THRESHOLD_LOW', 0.40))
    
    # Entity extraction confidence threshold
    ENTITY_CONFIDENCE_THRESHOLD = 0.7
    
    # Fuzzy matching threshold
    FUZZY_MATCH_THRESHOLD = 80
    
    # Weight for different matching parameters
    MATCH_WEIGHTS = {
        "truck_type": 0.25,      # 25%
        "tonnage": 0.20,         # 20%
        "length": 0.15,          # 15%
        "route_from": 0.15,      # 15%
        "route_to": 0.10,        # 10%
        "product": 0.10,         # 10%
        "availability": 0.05     # 5%
    }