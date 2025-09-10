import re
import json
from typing import Dict, List, Optional, Tuple
from fuzzywuzzy import fuzz
from models.transcript_model import Transcript
from models.entities_model import ExtractedEntities, TruckType
from utils.text_processing import TextProcessor
from utils.fuzzy_matching import FuzzyMatcher
import logging

class EntityExtractionAgent:
    """
    Agent responsible for extracting trucking-related entities from conversation transcripts.
    Handles multilingual content and local language nuances.
    """
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.fuzzy_matcher = FuzzyMatcher()
        self.logger = logging.getLogger(__name__)
        
        # Initialize extraction patterns and vocabularies
        self._setup_patterns()
        self._setup_vocabularies()
    
    def _setup_patterns(self):
        """Setup regex patterns for entity extraction"""
        # Truck specifications patterns
        self.truck_length_pattern = re.compile(r'(\d+)\s*(?:feet?|ft|foot)', re.IGNORECASE)
        self.tonnage_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*(?:tons?|ton|mt|tonnes?)', re.IGNORECASE)
        self.phone_pattern = re.compile(r'(?:\+91|91)?[6-9]\d{9}')
        self.price_pattern = re.compile(r'(?:₹|rs\.?|rupees?|rate|rent)\s*(\d+(?:,\d+)*(?:\.\d+)?)', re.IGNORECASE)
        
        # Location patterns (Indian cities/states)
        self.location_pattern = re.compile(r'\b(?:bangalore|bengaluru|hyderabad|chennai|mumbai|delhi|kolkata|pune|jaipur|ahmedabad)\b', re.IGNORECASE)
        
        # PIN code pattern
        self.pincode_pattern = re.compile(r'\b\d{6}\b')
    
    def _setup_vocabularies(self):
        """Setup vocabularies for fuzzy matching"""
        # Truck type vocabularies with variations and misspellings
        self.truck_type_vocab = {
            'open': ['open', 'open truck', 'open vehicle', 'open body', 'goods vehicle'],
            'container': ['container', 'closed', 'closed vehicle', 'cantener', 'containr'],
            'multi_axle': ['multi axle', 'multi-axle', 'mxl', 'multiaxle'],
            'single_axle': ['single axle', 'single-axle', 'sxl', 'single axel', 'singleaxle']
        }
        
        # Product vocabularies
        self.product_vocab = {
            'pipes': ['pipe', 'pipes', 'pipeline', 'tubes'],
            'cotton': ['cotton', 'cotton boxes', 'cotton bales'],
            'steel': ['steel', 'iron', 'metal'],
            'cement': ['cement', 'concrete']
        }
        
        # Location vocabularies with common variations
        self.location_vocab = {
            'bangalore': ['bangalore', 'bengaluru', 'blr', 'banglore'],
            'hyderabad': ['hyderabad', 'hyd', 'secunderabad', 'cyberabad'],
            'chennai': ['chennai', 'madras'],
            'mumbai': ['mumbai', 'bombay'],
            'vijayawada': ['vijayawada', 'vijayawada'],
            'jigani': ['jigani'],
            'nelmangala': ['nelmangala', 'nelamangala'],
            'attibele': ['attibele'],
            'tumkur': ['tumkur', 'tumkuru']
        }
        
        # Time/availability vocabularies
        self.time_vocab = {
            'immediate': ['immediately', 'now', 'today', 'same day'],
            'tomorrow': ['tomorrow', 'next day'],
            'monday': ['monday', 'mon'],
            'sunday': ['sunday', 'sun'],
            'weekend': ['weekend', 'saturday', 'sunday']
        }
    
    def extract_entities(self, transcript: Transcript) -> ExtractedEntities:
        """
        Main method to extract entities from transcript
        """
        # Combine all conversation text
        full_text = self._combine_conversation_text(transcript)
        
        # Extract different types of entities
        truck_specs = self._extract_truck_specifications(full_text, transcript.turns)
        locations = self._extract_locations(full_text)
        commercial_terms = self._extract_commercial_terms(full_text, transcript.turns)
        availability = self._extract_availability(full_text)
        contact_info = self._extract_contact_info(full_text)
        
        # Calculate confidence scores
        confidence_scores = self._calculate_confidence_scores(
            truck_specs, locations, commercial_terms, availability, contact_info
        )
        
        # Build ExtractedEntities object
        entities = ExtractedEntities(
            truck_type=truck_specs.get('type'),
            truck_length=truck_specs.get('length'),
            tonnage=truck_specs.get('tonnage'),
            current_location=locations.get('current'),
            preferred_routes=locations.get('routes', []),
            expected_rate=commercial_terms.get('rate'),
            rate_flexibility=commercial_terms.get('flexibility'),
            available_immediately=availability.get('immediate', True),
            availability_constraints=availability.get('constraints', []),
            phone_number=contact_info.get('phone'),
            special_requirements=truck_specs.get('special_requirements', []),
            confidence_scores=confidence_scores
        )
        
        self.logger.info(f"Extracted entities with overall confidence: {confidence_scores.get('overall', 0)}")
        return entities
    
    def _combine_conversation_text(self, transcript: Transcript) -> str:
        """Combine all conversation turns into single text"""
        return " ".join([turn.text for turn in transcript.turns])
    
    def _extract_truck_specifications(self, text: str, turns: List) -> Dict:
        """Extract truck type, length, tonnage, and special requirements"""
        truck_specs = {}
        
        # Extract truck type using fuzzy matching
        truck_type = self._fuzzy_match_truck_type(text)
        if truck_type:
            truck_specs['type'] = truck_type
        
        # Extract length
        length_match = self.truck_length_pattern.search(text)
        if length_match:
            truck_specs['length'] = int(length_match.group(1))
        
        # Extract tonnage
        tonnage_match = self.tonnage_pattern.search(text)
        if tonnage_match:
            tonnage_str = tonnage_match.group(1).replace(',', '')
            truck_specs['tonnage'] = float(tonnage_str)
        
        # Extract special requirements
        special_reqs = []
        if 'tarpaulin' in text.lower() or 'tarp' in text.lower():
            special_reqs.append('tarpaulin_required')
        if 'expenses' in text.lower():
            special_reqs.append('expenses_included')
        
        truck_specs['special_requirements'] = special_reqs
        
        return truck_specs
    
    def _fuzzy_match_truck_type(self, text: str) -> Optional[TruckType]:
        """Use fuzzy matching to identify truck type from text"""
        text_lower = text.lower()
        best_match = None
        best_score = 0
        
        for truck_type, variations in self.truck_type_vocab.items():
            for variation in variations:
                # Check if variation appears in text
                if variation in text_lower:
                    return TruckType(truck_type.replace('_', '_'))
                
                # Fuzzy match
                score = fuzz.partial_ratio(variation, text_lower)
                if score > 80 and score > best_score:  # Threshold for fuzzy match
                    best_score = score
                    best_match = truck_type
        
        return TruckType(best_match.replace('_', '_')) if best_match else None
    
    def _extract_locations(self, text: str) -> Dict:
        """Extract current location and preferred routes"""
        locations = {'routes': []}
        
        # Find all potential locations using fuzzy matching
        found_locations = []
        text_lower = text.lower()
        
        for standard_location, variations in self.location_vocab.items():
            for variation in variations:
                if variation in text_lower:
                    found_locations.append(standard_location)
                    break
        
        # Also find PIN codes and try to map them
        pincode_matches = self.pincode_pattern.findall(text)
        
        # Simple heuristic: first location mentioned might be current location
        if found_locations:
            locations['current'] = found_locations[0]
            locations['routes'] = found_locations
        
        return locations
    
    def _extract_commercial_terms(self, text: str, turns: List) -> Dict:
        """Extract pricing and commercial terms"""
        commercial = {}
        
        # Extract price/rate
        price_match = self.price_pattern.search(text)
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            commercial['rate'] = float(price_str)
        
        # Determine rate flexibility based on conversation tone
        if any(word in text.lower() for word in ['negotiate', 'discuss', 'ask', 'tell rate']):
            commercial['flexibility'] = 'negotiable'
        elif any(word in text.lower() for word in ['fixed', 'confirmed', 'final']):
            commercial['flexibility'] = 'fixed'
        else:
            commercial['flexibility'] = 'unknown'
        
        return commercial
    
    def _extract_availability(self, text: str) -> Dict:
        """Extract availability and timing constraints"""
        availability = {}
        constraints = []
        
        text_lower = text.lower()
        
        # Check for immediate availability
        if any(word in text_lower for word in ['immediately', 'now', 'today', 'same day']):
            availability['immediate'] = True
        else:
            availability['immediate'] = False
        
        # Check for day constraints
        if 'sunday' in text_lower and 'not' in text_lower:
            constraints.append('no_sunday_unloading')
        
        if 'monday' in text_lower:
            constraints.append('monday_delivery')
        
        availability['constraints'] = constraints
        return availability
    
    def _extract_contact_info(self, text: str) -> Dict:
        """Extract phone numbers and contact information"""
        contact = {}
        
        phone_matches = self.phone_pattern.findall(text)
        if phone_matches:
            # Take the longest/most complete number
            contact['phone'] = max(phone_matches, key=len)
        
        return contact
    
    def _calculate_confidence_scores(self, truck_specs: Dict, locations: Dict, 
                                   commercial: Dict, availability: Dict, 
                                   contact: Dict) -> Dict[str, float]:
        """Calculate confidence scores for extracted entities"""
        scores = {}
        
        # Individual entity confidence scores
        scores['truck_type'] = 0.9 if truck_specs.get('type') else 0.0
        scores['truck_length'] = 0.95 if truck_specs.get('length') else 0.0
        scores['tonnage'] = 0.95 if truck_specs.get('tonnage') else 0.0
        scores['location'] = 0.8 if locations.get('current') else 0.3
        scores['rate'] = 0.9 if commercial.get('rate') else 0.0
        scores['phone'] = 0.95 if contact.get('phone') else 0.0
        scores['availability'] = 0.7  # Always some indication from conversation
        
        # Overall confidence (weighted average of critical entities)
        critical_entities = ['truck_type', 'tonnage', 'location']
        critical_scores = [scores.get(entity, 0) for entity in critical_entities]
        scores['overall'] = sum(critical_scores) / len(critical_scores) if critical_scores else 0.0
        
        return scores