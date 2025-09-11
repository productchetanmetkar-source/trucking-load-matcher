#!/usr/bin/env python3
"""
Main orchestrator for the Trucking Load Matching System
"""

import time
from typing import List, Optional
from datetime import datetime

# Import your existing components
from agents.entity_extraction_agent import EntityExtractionAgent
from agents.load_matching_agent import LoadMatchingAgent
from models.transcript_model import Transcript, ConversationTurn
from models.load_model import Load, LoadStatus
from models.entities_model import ExtractedEntities, TruckType


class MatchResult:
    """Result of the load matching process"""
    
    def __init__(self, extracted_entities: ExtractedEntities, load_matches: List, 
                 business_recommendation: str, reasoning: str = ""):
        self.extracted_entities = extracted_entities
        self.load_matches = load_matches
        self.business_recommendation = business_recommendation
        self.reasoning = reasoning
        self.timestamp = time.time()


class TruckingLoadMatcher:
    """
    Main orchestrator class for the trucking load matching system
    """
    
    def __init__(self):
        """Initialize the matcher with required agents"""
        self.entity_agent = EntityExtractionAgent()
        self.load_agent = LoadMatchingAgent()
        self.processing_history = []
        
    def process_transcript(self, transcript: Transcript, available_loads: List[Load]) -> MatchResult:
        """
        Process a transcript and match with available loads
        """
        
        try:
            # Step 1: Extract entities from transcript
            print(f"🔍 Extracting entities from transcript...")
            extracted_entities = self.entity_agent.extract_entities(transcript)
            
            if not extracted_entities:
                return MatchResult(
                    extracted_entities=ExtractedEntities(),
                    load_matches=[],
                    business_recommendation="reject",
                    reasoning="Could not extract any meaningful entities from transcript"
                )
            
            # Step 2: Match with available loads
            print(f"🎯 Matching with {len(available_loads)} available loads...")
            # Use the correct method name from your LoadMatchingAgent
            load_matches = self.load_agent.find_matching_loads(extracted_entities, available_loads)
            
            # Step 3: Determine business recommendation
            business_recommendation, reasoning = self._determine_business_action(
                extracted_entities, load_matches
            )
            
            # Step 4: Create and store result
            result = MatchResult(
                extracted_entities=extracted_entities,
                load_matches=load_matches,
                business_recommendation=business_recommendation,
                reasoning=reasoning
            )
            
            print(f"✅ Processing completed: {business_recommendation}")
            return result
            
        except Exception as e:
            print(f"❌ Error processing transcript: {e}")
            import traceback
            traceback.print_exc()
            return MatchResult(
                extracted_entities=ExtractedEntities(),
                load_matches=[],
                business_recommendation="reject",
                reasoning=f"Processing error: {str(e)}"
            )
    
    def _determine_business_action(self, entities: ExtractedEntities, matches: List) -> tuple:
        """Determine the business action based on extracted entities and matches"""
        
        if not matches:
            # Check if we have good entity extraction
            has_truck_info = entities.truck_type is not None or entities.tonnage is not None
            has_location_info = entities.current_location is not None or len(entities.preferred_routes) > 0
            
            if not has_truck_info and not has_location_info:
                return "reject", "Insufficient information extracted from transcript"
            else:
                return "create_lead", "Good entity extraction but no current matches - create lead for future"
        
        # Check best match score
        best_match = max(matches, key=lambda x: x.overall_score)
        
        if best_match.overall_score >= 0.8:
            return "auto_approve", f"High confidence match found ({best_match.overall_score:.1%})"
        elif best_match.overall_score >= 0.6:
            return "human_review", f"Good match found ({best_match.overall_score:.1%}) but requires human review"
        elif best_match.overall_score >= 0.4:
            return "create_lead", f"Moderate match ({best_match.overall_score:.1%}) - create lead for follow-up"
        else:
            return "reject", f"Low match scores (best: {best_match.overall_score:.1%})"


# Alias for backward compatibility with test files
TruckingMatchingOrchestrator = TruckingLoadMatcher


def create_sample_loads() -> List[Load]:
    """Create sample loads for testing"""
    
    return [
        Load(
            id="L001",
            booking_office="Chennai Office",
            message_id="MSG001", 
            timestamp=datetime.now(),
            from_location="Chennai",
            to_location="Bangalore",
            truck_type="Container",
            truck_length="20",
            tonnage="20",
            product="General Cargo", 
            price=25000.0,
            num_trucks=1,
            eta="2 days",
            status=LoadStatus.AVAILABLE
        ),
        Load(
            id="L002",
            booking_office="Mumbai Office",
            message_id="MSG002",
            timestamp=datetime.now(), 
            from_location="Mumbai",
            to_location="Coimbatore",
            truck_type="Open",
            truck_length="25",
            tonnage="15",
            product="Textiles",
            price=18000.0,
            num_trucks=1,
            eta="1 day",
            status=LoadStatus.AVAILABLE
        ),
        Load(
            id="L003",
            booking_office="Tumakuru Office",
            message_id="MSG003",
            timestamp=datetime.now(),
            from_location="Tumakuru", 
            to_location="Madurai",
            truck_type="Open",
            truck_length="25",
            tonnage="25",
            product="Agriculture",
            price=22000.0,
            num_trucks=1,
            eta="3 days",
            status=LoadStatus.AVAILABLE
        )
    ]


def main():
    """Main function for testing the system"""
    
    print("🚛 Trucking Load Matcher - Testing")
    print("=" * 50)
    
    try:
        # Initialize the matcher
        matcher = TruckingLoadMatcher()
        
        # Test transcript with proper turns structure
        conversation_text = "I have a 25 feet open vehicle. If there's anything towards Tamil Nadu side, like Madurai or Coimbatore, tell me if there's anyone on this road, I'll arrange it for you. From Tumakuru? Yes, let's arrange from Tumakuru. Kabbira"
        
        test_transcript = Transcript(
            conversation_text=conversation_text,
            turns=[
                ConversationTurn(
                    speaker="trucker", 
                    text=conversation_text,
                    timestamp=time.time()
                )
            ]
        )
        
        # Create sample loads
        sample_loads = create_sample_loads()
        print(f"✅ Created {len(sample_loads)} sample loads")
        
        # Process the transcript
        result = matcher.process_transcript(test_transcript, sample_loads)
        
        # Display results using correct field names
        print(f"\n🔍 Extracted Entities:")
        print(f"   Truck Type: {result.extracted_entities.truck_type}")
        print(f"   Truck Length: {result.extracted_entities.truck_length}")
        print(f"   Tonnage: {result.extracted_entities.tonnage}")
        print(f"   Current Location: {result.extracted_entities.current_location}")
        print(f"   Preferred Routes: {result.extracted_entities.preferred_routes}")
        print(f"   Expected Rate: {result.extracted_entities.expected_rate}")
        
        print(f"\n🎯 Load Matches: {len(result.load_matches)}")
        for i, match in enumerate(result.load_matches[:3]):  # Show top 3
            print(f"   {i+1}. Load {match.load_id} - Score: {match.overall_score:.1%}")
        
        print(f"\n💼 Business Recommendation: {result.business_recommendation}")
        print(f"   Reasoning: {result.reasoning}")
        
        print(f"\n✅ System test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()