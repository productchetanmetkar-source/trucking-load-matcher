from knowledge.trucking_knowledge import trucking_knowledge
import json
import re
from typing import Dict, List, Optional, Tuple
from fuzzywuzzy import fuzz
from models.transcript_model import Transcript
from models.entities_model import ExtractedEntities, TruckType
from utils.text_processing import TextProcessor
from utils.fuzzy_matching import FuzzyMatcher
import logging

class EntityExtractionAgent:
    """
    Enhanced Entity Extraction Agent for capturing both deterministic 
    and conversational entities from trucking conversations
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
        # Enhanced phone number patterns to catch fragmented numbers
        self.phone_pattern = re.compile(r'(?:\+91|91)?[6-9]\d{9}')
        self.fragmented_phone_pattern = re.compile(r'(\d{2,3})\.{2,3}(\d{3,4})\.{2,3}(\d{2,3})\.{2,3}(\d{2,3})\.{2,3}(\d{2,3})')
        self.number_sequence_pattern = re.compile(r'\b\d{2,4}\b')
        
        # Price patterns with more variations
        self.price_pattern = re.compile(r'(?:₹|rs\.?|rupees?|rate|rent|price|amount)\s*(\d+(?:,\d+)*(?:\.\d+)?)', re.IGNORECASE)
        self.quoted_price_pattern = re.compile(r'(?:quote|quoted|offer|charge)\s*(?:₹|rs\.?|rupees?)?\s*(\d+(?:,\d+)*)', re.IGNORECASE)
        
        # Truck specifications patterns
        self.truck_length_pattern = re.compile(r'(\d+)\s*(?:feet?|ft|foot)', re.IGNORECASE)
        self.tonnage_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*(?:tons?|ton|mt|tonnes?|capacity)', re.IGNORECASE)
        
        # Location patterns
        self.location_pattern = re.compile(r'\b(?:from|to|going|coming|pickup|drop|delivery)\s+([A-Za-z\s]+?)(?:\s|$|[,.])', re.IGNORECASE)
        
        # Conversational intent patterns
        self.load_pitch_patterns = [
            r'(?:we have|got|available)\s+(?:a|one)?\s*load',
            r'load\s+(?:is\s+)?available',
            r'there\s+(?:is\s+)?(?:a\s+)?load',
            r'load\s+for\s+you'
        ]
        
        self.no_load_patterns = [
            r'no\s+load\s+available',
            r'don\'t\s+have\s+(?:any\s+)?load',
            r'no\s+load\s+(?:right\s+now|currently)',
            r'sorry.*no\s+load'
        ]
        
        self.price_discussion_patterns = [
            r'what\s+(?:is\s+the\s+)?(?:rate|price|amount)',
            r'how\s+much',
            r'tell\s+me\s+(?:the\s+)?(?:rate|price)',
            r'rate\s+(?:is\s+)?what'
        ]
    
    def _setup_vocabularies(self):
        """Enhanced vocabularies with conversation context"""
        self.truck_type_vocab = {
            'open': ['open', 'open truck', 'open vehicle', 'open body', 'goods vehicle', 'half body'],
            'container': ['container', 'closed', 'closed vehicle', 'full body', 'cantener', 'containr', 'box'],
            'multi_axle': ['multi axle', 'multi-axle', 'mxl', 'multiaxle', 'trailer'],
            'single_axle': ['single axle', 'single-axle', 'sxl', 'single axel']
        }
        
        self.location_vocab = {
            'bangalore': ['bangalore', 'bengaluru', 'blr', 'banglore'],
            'hyderabad': ['hyderabad', 'hyd', 'secunderabad', 'cyberabad'],
            'chennai': ['chennai', 'madras', 'channai'],
            'mumbai': ['mumbai', 'bombay', 'mumbay'],
            'coimbatore': ['coimbatore', 'kovai', 'coimbtore'],
            'madurai': ['madurai', 'mathurai'],
            'tumakuru': ['tumakuru', 'tumkur', 'tumkuru'],
            'gujarat': ['gujarat', 'gujrat', 'gujarath']
        }
        
        # Speaker identification patterns
        self.fo_indicators = ['trucker', 'fo', 'field officer', 'driver']
        self.shipper_indicators = ['shipper', 'client', 'customer', 'booking']
        self.ti_indicators = ['ti', 'traffic incharge', 'operator', 'agent']
    
    def extract_entities(self, transcript: Transcript) -> ExtractedEntities:
        """
        Enhanced entity extraction with deterministic and conversational entities
        """
        # Parse conversation into structured data
        conversation_data = self._parse_conversation(transcript)
        
        # Extract deterministic entities
        deterministic_entities = self._extract_deterministic_entities(conversation_data)
        
        # Extract conversational entities
        conversational_entities = self._extract_conversational_entities(conversation_data)
        
        # Combine and create ExtractedEntities object
        entities = self._build_entities_object(deterministic_entities, conversational_entities)
        
        # Apply knowledge base normalization
        entities = self._apply_knowledge_normalization(entities, conversation_data['full_text'])
        
        return entities
    
    def _parse_conversation(self, transcript: Transcript) -> Dict:
        """Parse conversation into structured format for analysis"""
        conversation_data = {
            'turns': [],
            'full_text': '',
            'fo_turns': [],
            'shipper_turns': [],
            'ti_turns': []
        }
        
        # Combine all conversation text
        full_text_parts = []
        
        for turn in transcript.turns:
            speaker = turn.speaker.lower()
            text = turn.text
            
            turn_data = {
                'speaker': speaker,
                'text': text,
                'speaker_type': self._identify_speaker_type(speaker, text)
            }
            
            conversation_data['turns'].append(turn_data)
            full_text_parts.append(f"{speaker}: {text}")
            
            # Categorize by speaker type
            if turn_data['speaker_type'] == 'fo':
                conversation_data['fo_turns'].append(turn_data)
            elif turn_data['speaker_type'] == 'shipper':
                conversation_data['shipper_turns'].append(turn_data)
            elif turn_data['speaker_type'] == 'ti':
                conversation_data['ti_turns'].append(turn_data)
        
        conversation_data['full_text'] = '\n'.join(full_text_parts)
        return conversation_data
    
    def _identify_speaker_type(self, speaker: str, text: str) -> str:
        """Identify if speaker is FO, Shipper, or TI based on context"""
        speaker_lower = speaker.lower()
        text_lower = text.lower()
        
        # Check explicit indicators
        if any(indicator in speaker_lower for indicator in self.fo_indicators):
            return 'fo'
        if any(indicator in speaker_lower for indicator in self.shipper_indicators):
            return 'shipper'
        if any(indicator in speaker_lower for indicator in self.ti_indicators):
            return 'ti'
        
        # Special case: if speaker is "trucker", classify as FO
        if 'trucker' in speaker_lower:
            return 'fo'
        
        # Special case: if speaker is "shipper", classify as shipper/ti
        if 'shipper' in speaker_lower:
            return 'ti'  # Treating shipper as TI for conversation analysis
        
        # Infer from content patterns
        if any(phrase in text_lower for phrase in ['my truck', 'our vehicle', 'we have truck']):
            return 'fo'
        if any(phrase in text_lower for phrase in ['load available', 'we have load', 'rate is']):
            return 'ti'
        if any(phrase in text_lower for phrase in ['need truck', 'want vehicle', 'cargo to move']):
            return 'shipper'
        
        # Default: if we can't identify, assume it's part of the conversation
        return 'unknown'
    
    def _extract_deterministic_entities(self, conversation_data: Dict) -> Dict:
        """Extract deterministic entities: locations, truck specs, prices, numbers"""
        entities = {
            'fo_from_location': None,
            'fo_to_location': None,
            'fo_truck_type': None,
            'fo_tonnage': None,
            'fo_truck_length': None,
            'shipper_quoted_price': None,
            'fo_quoted_price': None,
            'fo_shared_number': None
        }
        
        # Extract from FO turns
        fo_text = ' '.join([turn['text'] for turn in conversation_data['fo_turns']])
        if fo_text:
            entities.update(self._extract_from_fo_speech(fo_text))
        
        # Extract from Shipper/TI turns
        shipper_text = ' '.join([turn['text'] for turn in conversation_data['shipper_turns'] + conversation_data['ti_turns']])
        if shipper_text:
            entities.update(self._extract_from_shipper_speech(shipper_text))
        
        # Extract phone numbers from entire conversation
        entities['fo_shared_number'] = self._extract_phone_numbers(conversation_data['full_text'])
        
        return entities
    
    def _extract_from_fo_speech(self, fo_text: str) -> Dict:
        """Extract entities specifically from FO speech"""
        entities = {}
        
        # Extract truck specifications
        truck_type = self._fuzzy_match_truck_type(fo_text)
        if truck_type:
            entities['fo_truck_type'] = truck_type
        
        # Extract tonnage
        tonnage_match = self.tonnage_pattern.search(fo_text)
        if tonnage_match:
            entities['fo_tonnage'] = float(tonnage_match.group(1))
        
        # Extract length
        length_match = self.truck_length_pattern.search(fo_text)
        if length_match:
            entities['fo_truck_length'] = int(length_match.group(1))
        
        # Extract FO quoted price/rate expectations
        price_match = self.price_pattern.search(fo_text)
        if price_match:
            entities['fo_quoted_price'] = float(price_match.group(1).replace(',', ''))
        
        # Extract locations using enhanced pattern matching
        locations = self._extract_locations_enhanced(fo_text)
        if locations.get('from'):
            entities['fo_from_location'] = locations['from']
        if locations.get('to'):
            entities['fo_to_location'] = locations['to']
        
        return entities
    
    def _extract_from_shipper_speech(self, shipper_text: str) -> Dict:
        """Extract entities from Shipper/TI speech"""
        entities = {}
        
        # Extract shipper quoted price
        price_matches = list(self.price_pattern.finditer(shipper_text))
        quote_matches = list(self.quoted_price_pattern.finditer(shipper_text))
        
        if price_matches or quote_matches:
            # Take the first clear price mention
            all_matches = price_matches + quote_matches
            if all_matches:
                price_str = all_matches[0].group(1).replace(',', '')
                entities['shipper_quoted_price'] = float(price_str)
        
        return entities
    
    def _extract_phone_numbers(self, full_text: str) -> Optional[str]:
        """Enhanced phone number extraction including fragmented numbers"""
        # Try standard phone pattern first
        phone_matches = self.phone_pattern.findall(full_text)
        if phone_matches:
            return phone_matches[0]
        
        # Try fragmented phone pattern (like "98... 9867... 33... 74... 13")
        fragmented_match = self.fragmented_phone_pattern.search(full_text)
        if fragmented_match:
            # Reconstruct the number from fragments
            fragments = fragmented_match.groups()
            reconstructed = ''.join(fragments)
            # Validate it looks like a phone number
            if len(reconstructed) >= 10 and reconstructed[0] in '6789':
                return reconstructed
        
        # Try to find number sequences and reconstruct
        # Look for patterns like "98 9867 33 74 13" or similar
        number_sequences = self.number_sequence_pattern.findall(full_text)
        if len(number_sequences) >= 3:
            # Try to reconstruct phone number from sequences
            potential_number = ''.join(number_sequences[:5])  # Take first 5 sequences
            if len(potential_number) >= 10 and potential_number[0] in '6789':
                return potential_number
        
        return None
    
    def _extract_locations_enhanced(self, text: str) -> Dict:
        """Enhanced location extraction with directional context"""
        locations = {'from': None, 'to': None}
        
        # Look for "from X to Y" patterns
        from_to_pattern = re.compile(r'from\s+([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+?)(?:\s|$|[,.])', re.IGNORECASE)
        from_to_match = from_to_pattern.search(text)
        
        if from_to_match:
            from_loc = from_to_match.group(1).strip()
            to_loc = from_to_match.group(2).strip()
            
            # Normalize using vocabulary
            locations['from'] = self._normalize_location(from_loc)
            locations['to'] = self._normalize_location(to_loc)
        else:
            # Look for individual location mentions with context
            location_matches = self.location_pattern.findall(text)
            normalized_locations = [self._normalize_location(loc) for loc in location_matches if loc.strip()]
            
            if len(normalized_locations) >= 2:
                locations['from'] = normalized_locations[0]
                locations['to'] = normalized_locations[1]
            elif len(normalized_locations) == 1:
                # Determine if it's from or to based on context
                if 'from' in text.lower():
                    locations['from'] = normalized_locations[0]
                elif 'to' in text.lower():
                    locations['to'] = normalized_locations[0]
        
        return locations
    
    def _normalize_location(self, location: str) -> str:
        """Normalize location using knowledge base"""
        location_clean = location.lower().strip()
        
        for standard_location, variations in self.location_vocab.items():
            if location_clean in variations or any(var in location_clean for var in variations):
                return standard_location.title()
        
        return location.strip().title()
    
    def _extract_conversational_entities(self, conversation_data: Dict) -> Dict:
        """Extract conversational intent entities"""
        entities = {
            'did_ti_pitch_load': False,
            'was_price_discussed': False,
            'did_ti_say_no_load': False,
            'was_number_exchanged': False
        }
        
        full_text = conversation_data['full_text'].lower()
        
        # Check if TI pitched any load
        for pattern in self.load_pitch_patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                entities['did_ti_pitch_load'] = True
                break
        
        # Additional load pitch detection
        if any(phrase in full_text for phrase in ['load for gujarat', 'load of yours', 'load available']):
            entities['did_ti_pitch_load'] = True
        
        # Check if price was discussed
        for pattern in self.price_discussion_patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                entities['was_price_discussed'] = True
                break
        
        # Also check if any price numbers were mentioned or capacity discussed
        if (self.price_pattern.search(full_text) or 'rate' in full_text or 
            'capacity' in full_text or 'ton' in full_text):
            entities['was_price_discussed'] = True
        
        # Check if TI said no load available
        for pattern in self.no_load_patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                entities['did_ti_say_no_load'] = True
                break
        
        # Check if number was exchanged - Enhanced detection
        number_exchange_indicators = [
            'mobile number', 'phone number', 'your number', 'tell me your number',
            'give me your number', 'share your number'
        ]
        
        # Check for explicit number exchange conversation
        for indicator in number_exchange_indicators:
            if indicator in full_text:
                entities['was_number_exchanged'] = True
                break
        
        # Also check if we can actually find any numbers in the text
        if (re.search(r'\d{10}', full_text.replace(' ', '').replace('.', '').replace('-', '')) or
            self.fragmented_phone_pattern.search(full_text) or
            re.search(r'\d{2,3}\.{2,}\d{3,4}\.{2,}\d{2,3}\.{2,}\d{2,3}\.{2,}\d{2,3}', full_text)):
            entities['was_number_exchanged'] = True
        
        return entities
    
    def _fuzzy_match_truck_type(self, text: str) -> Optional[TruckType]:
        """Enhanced truck type matching with knowledge base"""
        text_lower = text.lower()
        
        for truck_type, variations in self.truck_type_vocab.items():
            for variation in variations:
                if variation in text_lower:
                    return getattr(TruckType, truck_type.upper())
                
                # Fuzzy match with threshold
                score = fuzz.partial_ratio(variation, text_lower)
                if score > 85:
                    return getattr(TruckType, truck_type.upper())
        
        return None
    
    def _build_entities_object(self, deterministic: Dict, conversational: Dict) -> ExtractedEntities:
        """Build ExtractedEntities object from extracted data"""
        confidence_scores = {}
        
        # Calculate confidence scores
        for key, value in deterministic.items():
            if value is not None:
                confidence_scores[key] = 0.9
        
        for key, value in conversational.items():
            confidence_scores[key] = 0.8
        
        # Calculate overall confidence
        if confidence_scores:
            confidence_scores['overall'] = sum(confidence_scores.values()) / len(confidence_scores)
        
        # Create entity object with ALL fields explicitly set
        entities = ExtractedEntities(
            # Original fields
            truck_type=deterministic.get('fo_truck_type'),
            truck_length=deterministic.get('fo_truck_length'),
            tonnage=deterministic.get('fo_tonnage'),
            current_location=deterministic.get('fo_from_location'),
            preferred_routes=[loc for loc in [deterministic.get('fo_from_location'), 
                                            deterministic.get('fo_to_location')] if loc],
            expected_rate=deterministic.get('fo_quoted_price'),
            phone_number=deterministic.get('fo_shared_number'),
            available_immediately=True,
            confidence_scores=confidence_scores,
            
            # Enhanced deterministic fields
            fo_from_location=deterministic.get('fo_from_location'),
            fo_to_location=deterministic.get('fo_to_location'),
            fo_truck_type=deterministic.get('fo_truck_type'),
            fo_tonnage=deterministic.get('fo_tonnage'),
            fo_truck_length=deterministic.get('fo_truck_length'),
            shipper_quoted_price=deterministic.get('shipper_quoted_price'),
            fo_quoted_price=deterministic.get('fo_quoted_price'),
            fo_shared_number=deterministic.get('fo_shared_number'),
            
            # Enhanced conversational fields
            did_ti_pitch_load=conversational.get('did_ti_pitch_load', False),
            was_price_discussed=conversational.get('was_price_discussed', False),
            did_ti_say_no_load=conversational.get('did_ti_say_no_load', False),
            was_number_exchanged=conversational.get('was_number_exchanged', False),
            
            # Backup in special_requirements
            special_requirements=[
                f"fo_shared_number:{deterministic.get('fo_shared_number')}",
                f"shipper_quoted_price:{deterministic.get('shipper_quoted_price')}",
                f"did_ti_pitch_load:{conversational.get('did_ti_pitch_load')}",
                f"was_price_discussed:{conversational.get('was_price_discussed')}",
                f"did_ti_say_no_load:{conversational.get('did_ti_say_no_load')}",
                f"was_number_exchanged:{conversational.get('was_number_exchanged')}"
            ]
        )
        print(f"DEBUG: Setting fo_shared_number to: {deterministic.get('fo_shared_number')}")
        print(f"DEBUG: Setting was_number_exchanged to: {conversational.get('was_number_exchanged')}")
        return entities
    
    def _apply_knowledge_normalization(self, entities: ExtractedEntities, full_text: str) -> ExtractedEntities:
        """Apply knowledge base normalization"""
        if hasattr(trucking_knowledge, 'get_knowledge_context'):
            knowledge_context = trucking_knowledge.get_knowledge_context()
            
            # Normalize truck type using knowledge base
            if full_text:
                for standard_type, data in knowledge_context['truck_classifications'].items():
                    aliases = data.get('aliases', [])
                    for alias in aliases:
                        if alias.lower() in full_text.lower():
                            if standard_type == 'container':
                                entities.truck_type = TruckType.CONTAINER
                            elif standard_type == 'open':
                                entities.truck_type = TruckType.OPEN
                            break
            
            # Normalize locations
            if entities.current_location:
                entities.current_location = trucking_knowledge.normalize_location(entities.current_location)
            
            if entities.preferred_routes:
                normalized_routes = []
                for route in entities.preferred_routes:
                    normalized_routes.append(trucking_knowledge.normalize_location(route))
                entities.preferred_routes = normalized_routes
        
        return entities