import json
import math
from typing import List, Dict, Tuple, Optional
from fuzzywuzzy import fuzz
from models.load_model import Load, LoadStatus
from models.entities_model import ExtractedEntities, MatchingResult
from utils.fuzzy_matching import FuzzyMatcher
from config import Config
import logging

class LoadMatchingAgent:
    """
    Agent responsible for matching trucker requirements with available loads.
    Calculates compatibility scores and provides recommendations.
    """
    
    def __init__(self):
        self.fuzzy_matcher = FuzzyMatcher(threshold=Config.FUZZY_MATCH_THRESHOLD)
        self.logger = logging.getLogger(__name__)
        self.config = Config()
        
        # Load truck compatibility matrix
        self._setup_compatibility_rules()
    
    def _setup_compatibility_rules(self):
        """Setup compatibility rules between truck types and load requirements"""
        # Truck type compatibility matrix
        self.truck_compatibility = {
            'open': {
                'compatible_with': ['open truck', 'open', 'goods vehicle'],
                'incompatible_with': ['container'],
                'flexible_with': []
            },
            'container': {
                'compatible_with': ['container', 'closed'],
                'incompatible_with': ['open truck', 'open'],
                'flexible_with': []
            }
        }
        
        # Product-truck compatibility
        self.product_truck_compatibility = {
            'ashirwad pipes': {
                'preferred': ['open', 'container'],
                'acceptable': ['open truck'],
                'avoid': []
            },
            'cotton boxes': {
                'preferred': ['open', 'open truck'],
                'acceptable': ['container'],
                'avoid': []
            }
        }
        
        # Tonnage tolerance (percentage)
        self.tonnage_tolerance = 0.2  # 20% tolerance
        
        # Length tolerance (feet)
        self.length_tolerance = 2  # 2 feet tolerance
    
    def find_matching_loads(self, trucker_requirements: ExtractedEntities, 
                          available_loads: List[Load]) -> List[MatchingResult]:
        """
        Find all loads that match trucker requirements and return sorted by match score
        """
        matching_results = []
        
        for load in available_loads:
            # Skip unavailable loads
            if load.status != LoadStatus.AVAILABLE:
                continue
            
            # Calculate match score
            match_result = self._calculate_match_score(trucker_requirements, load)
            
            if match_result.overall_score > 0:  # Only include positive matches
                matching_results.append(match_result)
        
        # Sort by overall score (descending)
        matching_results.sort(key=lambda x: x.overall_score, reverse=True)
        
        self.logger.info(f"Found {len(matching_results)} matching loads")
        return matching_results
    
    def _calculate_match_score(self, trucker_req: ExtractedEntities, load: Load) -> MatchingResult:
        """
        Calculate detailed match score between trucker requirements and load
        """
        detailed_scores = {}
        match_reasons = []
        mismatch_reasons = []
        
        # 1. Truck Type Matching (25% weight)
        truck_type_score = self._match_truck_type(trucker_req.truck_type, load.truck_type)
        detailed_scores['truck_type'] = truck_type_score
        
        if truck_type_score > 0.8:
            match_reasons.append(f"Truck type '{trucker_req.truck_type}' matches load requirement '{load.truck_type}'")
        elif truck_type_score < 0.3:
            mismatch_reasons.append(f"Truck type mismatch: trucker has '{trucker_req.truck_type}', load needs '{load.truck_type}'")
        
        # 2. Tonnage Matching (20% weight)
        tonnage_score = self._match_tonnage(trucker_req.tonnage, load.tonnage)
        detailed_scores['tonnage'] = tonnage_score
        
        if tonnage_score > 0.8:
            match_reasons.append(f"Tonnage capacity {trucker_req.tonnage}T suitable for {load.tonnage}T load")
        elif tonnage_score < 0.3:
            mismatch_reasons.append(f"Tonnage mismatch: trucker capacity {trucker_req.tonnage}T, load needs {load.tonnage}T")
        
        # 3. Length Matching (15% weight)
        length_score = self._match_length(trucker_req.truck_length, load.truck_length)
        detailed_scores['length'] = length_score
        
        # 4. Route Matching (15% weight - from + to locations)
        route_from_score = self._match_location(trucker_req.preferred_routes, load.from_location)
        route_to_score = self._match_location(trucker_req.preferred_routes, load.to_location)
        detailed_scores['route_from'] = route_from_score
        detailed_scores['route_to'] = route_to_score
        
        if route_from_score > 0.7:
            match_reasons.append(f"Pickup location '{load.from_location}' matches trucker's preferred routes")
        
        # 5. Product Compatibility (10% weight)
        product_score = self._match_product(trucker_req.truck_type, load.product)
        detailed_scores['product'] = product_score
        
        # 6. Availability (5% weight)
        availability_score = self._match_availability(trucker_req, load)
        detailed_scores['availability'] = availability_score
        
        # Calculate overall score using weighted average
        overall_score = (
            detailed_scores['truck_type'] * self.config.MATCH_WEIGHTS['truck_type'] +
            detailed_scores['tonnage'] * self.config.MATCH_WEIGHTS['tonnage'] +
            detailed_scores['length'] * self.config.MATCH_WEIGHTS['length'] +
            detailed_scores['route_from'] * self.config.MATCH_WEIGHTS['route_from'] +
            detailed_scores['route_to'] * self.config.MATCH_WEIGHTS['route_to'] +
            detailed_scores['product'] * self.config.MATCH_WEIGHTS['product'] +
            detailed_scores['availability'] * self.config.MATCH_WEIGHTS['availability']
        )
        
        # Determine recommendation
        recommendation = self._get_recommendation(overall_score, trucker_req, load)
        
        # Check mandatory criteria
        mandatory_match = (
            detailed_scores['truck_type'] >= 0.5 and
            detailed_scores['tonnage'] >= 0.5
        )
        
        # Calculate price gap and negotiation likelihood
        price_gap = None
        negotiation_likelihood = 0.5
        
        if trucker_req.expected_rate and load.price:
            price_gap = abs(trucker_req.expected_rate - load.price)
            # Simple heuristic for negotiation likelihood based on price difference
            price_diff_pct = price_gap / load.price
            if price_diff_pct < 0.1:  # Within 10%
                negotiation_likelihood = 0.9
            elif price_diff_pct < 0.2:  # Within 20%
                negotiation_likelihood = 0.7
            else:
                negotiation_likelihood = 0.3
        
        return MatchingResult(
            load_id=load.id,
            trucker_requirements_id="temp_id",  # Would be set by calling code
            overall_score=overall_score,
            detailed_scores=detailed_scores,
            mandatory_match=mandatory_match,
            recommendation=recommendation,
            match_reasons=match_reasons,
            mismatch_reasons=mismatch_reasons,
            price_gap=price_gap,
            negotiation_likelihood=negotiation_likelihood
        )
    
    def _match_truck_type(self, trucker_type: Optional[str], load_truck_type: str) -> float:
        """Match truck types with fuzzy matching and compatibility rules"""
        if not trucker_type:
            return 0.0
        
        trucker_type_str = str(trucker_type).lower()
        load_type_str = load_truck_type.lower()
        
        # Direct string match
        if trucker_type_str in load_type_str or load_type_str in trucker_type_str:
            return 1.0
        
        # Fuzzy string matching
        fuzzy_score = fuzz.ratio(trucker_type_str, load_type_str) / 100.0
        if fuzzy_score > 0.8:
            return fuzzy_score
        
        # Check compatibility rules
        for truck_type, rules in self.truck_compatibility.items():
            if truck_type in trucker_type_str:
                if any(compat in load_type_str for compat in rules['compatible_with']):
                    return 0.9
                if any(incompat in load_type_str for incompat in rules['incompatible_with']):
                    return 0.1
                if any(flex in load_type_str for flex in rules['flexible_with']):
                    return 0.6
        
        return max(0.3, fuzzy_score)  # Minimum compatibility score
    
    def _match_tonnage(self, trucker_tonnage: Optional[float], load_tonnage: Optional[str]) -> float:
        """Match tonnage capacity with tolerance"""
        if not trucker_tonnage or not load_tonnage:
            return 0.5  # Neutral score if information missing
        
        try:
            # Parse load tonnage (handle formats like "8mt", "10", etc.)
            load_tonnage_clean = str(load_tonnage).lower().replace('mt', '').replace('tons', '').replace('ton', '').strip()
            if not load_tonnage_clean or load_tonnage_clean == '-':
                return 0.5
            
            load_tonnage_float = float(load_tonnage_clean)
            
            # Trucker capacity should be >= load requirement
            if trucker_tonnage >= load_tonnage_float:
                # Perfect match or slight overcapacity
                if trucker_tonnage <= load_tonnage_float * (1 + self.tonnage_tolerance):
                    return 1.0
                else:
                    # Significant overcapacity - still acceptable but not optimal
                    return 0.7
            else:
                # Undercapacity - check if within tolerance
                capacity_ratio = trucker_tonnage / load_tonnage_float
                if capacity_ratio >= (1 - self.tonnage_tolerance):
                    return 0.6  # Close enough, might work
                else:
                    return 0.1  # Too low capacity
        
        except (ValueError, TypeError):
            return 0.5  # Can't parse, neutral score
    
    def _match_length(self, trucker_length: Optional[int], load_length: Optional[str]) -> float:
        """Match truck length with tolerance"""
        if not trucker_length or not load_length:
            return 0.7  # Neutral-positive score if information missing
        
        try:
            # Parse load length
            load_length_clean = str(load_length).lower().replace('ft', '').replace('feet', '').strip()
            if not load_length_clean or load_length_clean == '-':
                return 0.7
            
            load_length_int = int(load_length_clean)
            
            # Exact match
            if trucker_length == load_length_int:
                return 1.0
            
            # Within tolerance
            length_diff = abs(trucker_length - load_length_int)
            if length_diff <= self.length_tolerance:
                return 0.9
            
            # Longer truck (usually acceptable)
            if trucker_length > load_length_int:
                if length_diff <= 5:  # Within 5 feet longer
                    return 0.8
                else:
                    return 0.6
            
            # Shorter truck (problematic)
            if trucker_length < load_length_int:
                if length_diff <= 2:  # Within 2 feet shorter
                    return 0.5
                else:
                    return 0.2
        
        except (ValueError, TypeError):
            return 0.7
    
    def _match_location(self, trucker_locations: List[str], load_location: str) -> float:
        """Match locations using fuzzy matching"""
        if not trucker_locations or not load_location:
            return 0.4  # Neutral score if no location info
        
        load_location_clean = load_location.lower().strip()
        best_score = 0.0
        
        for trucker_loc in trucker_locations:
            trucker_loc_clean = trucker_loc.lower().strip()
            
            # Direct substring match
            if trucker_loc_clean in load_location_clean or load_location_clean in trucker_loc_clean:
                return 1.0
            
            # Fuzzy match
            fuzzy_score = fuzz.ratio(trucker_loc_clean, load_location_clean) / 100.0
            best_score = max(best_score, fuzzy_score)
        
        return best_score
    
    def _match_product(self, trucker_truck_type: Optional[str], load_product: str) -> float:
        """Match product with truck type compatibility"""
        if not trucker_truck_type:
            return 0.6  # Neutral score
        
        truck_type_str = str(trucker_truck_type).lower()
        product_str = load_product.lower()
        
        # Check product-truck compatibility rules
        for product, compatibility in self.product_truck_compatibility.items():
            if product in product_str:
                if any(pref in truck_type_str for pref in compatibility['preferred']):
                    return 1.0
                if any(acc in truck_type_str for acc in compatibility['acceptable']):
                    return 0.7
                if any(avoid in truck_type_str for avoid in compatibility['avoid']):
                    return 0.2
        
        # Default compatibility
        return 0.6
    
    def _match_availability(self, trucker_req: ExtractedEntities, load: Load) -> float:
        """Match availability and timing constraints"""
        score = 0.8  # Base score
        
        # Check if trucker is available immediately and load needs immediate pickup
        if trucker_req.available_immediately and 'same day' in load.eta.lower():
            score = 1.0
        
        # Check for timing constraints
        for constraint in trucker_req.availability_constraints:
            if 'sunday' in constraint and 'sunday' in load.eta.lower():
                score *= 0.5  # Reduce score for timing conflicts
        
        return min(1.0, score)
    
    def _get_recommendation(self, overall_score: float, trucker_req: ExtractedEntities, load: Load) -> str:
        """Get recommendation based on match score and business rules"""
        
        # High confidence match
        if overall_score >= self.config.MATCH_THRESHOLD_HIGH:
            return "auto_approve"
        
        # Medium confidence - needs human review
        elif overall_score >= self.config.MATCH_THRESHOLD_MEDIUM:
            return "human_review"
        
        # Low confidence but still some interest
        elif overall_score >= self.config.MATCH_THRESHOLD_LOW:
            return "create_lead"
        
        # Very low match
        else:
            return "reject"

    def get_best_match(self, trucker_requirements: ExtractedEntities, 
                      available_loads: List[Load]) -> Optional[MatchingResult]:
        """Get the single best matching load"""
        matches = self.find_matching_loads(trucker_requirements, available_loads)
        return matches[0] if matches else None