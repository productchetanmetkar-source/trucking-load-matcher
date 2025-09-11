# main.py - Main orchestrator for the trucking load matching system
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from agents.entity_extraction_agent import EntityExtractionAgent
from agents.load_matching_agent import LoadMatchingAgent
from models.transcript_model import Transcript, ConversationTurn
from models.load_model import Load, LoadStatus
from models.entities_model import ExtractedEntities
from models.entities_model import MatchingResult

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TruckingMatchingOrchestrator:
    """
    Main orchestrator that coordinates the multi-agent system for load matching
    """
    
    def __init__(self):
        self.entity_extraction_agent = EntityExtractionAgent()
        self.load_matching_agent = LoadMatchingAgent()
        logger.info("Trucking Matching Orchestrator initialized")
    
    def process_call_transcript(self, transcript_data: Dict[str, Any], 
                              available_loads: List[Load]) -> Dict[str, Any]:
        """
        Main processing pipeline: transcript -> entities -> matching -> scoring
        """
        logger.info(f"Processing call transcript with {len(available_loads)} available loads")
        
        # Step 1: Parse transcript
        transcript = self._parse_transcript(transcript_data)
        
        # Step 2: Extract entities from transcript
        logger.info("Extracting entities from transcript...")
        # Try enhanced extraction with knowledge base first, fallback to regular
        if hasattr(self.entity_extraction_agent, 'extract_entities_with_knowledge'):
            extracted_entities = self.entity_extraction_agent.extract_entities_with_knowledge(transcript)
        else:
            extracted_entities = self.entity_extraction_agent.extract_entities(transcript)        
        # Step 3: Find matching loads
        logger.info("Finding matching loads...")
        matching_results = self.load_matching_agent.find_matching_loads(
            extracted_entities, available_loads
        )
        
        # Step 4: Prepare response
        response = {
            "transcript_id": transcript.id,
            "processing_timestamp": datetime.now().isoformat(),
            "extracted_entities": extracted_entities.model_dump(),
            "total_loads_checked": len(available_loads),
            "matches_found": len(matching_results),
            "best_match": matching_results[0].model_dump() if matching_results else None,
            "all_matches": [match.model_dump() for match in matching_results[:5]],
            "recommendation": self._get_overall_recommendation(matching_results, extracted_entities)
        }
        
        logger.info(f"Processing complete. Found {len(matching_results)} matches")
        return response
    
    def _parse_transcript(self, transcript_data: Dict[str, Any]) -> Transcript:
        """Parse transcript data into Transcript model"""
        turns = []
        for turn_data in transcript_data.get("conversation", []):
            turn = ConversationTurn(
                speaker=turn_data["speaker"],
                text=turn_data["text"],
                timestamp=turn_data.get("timestamp")
            )
            turns.append(turn)
        
        return Transcript(
            id=transcript_data.get("id", f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            turns=turns,
            call_duration=transcript_data.get("duration"),
            caller_number=transcript_data.get("caller_number"),
            language_detected=transcript_data.get("language", "mixed")
        )
    
    def _get_overall_recommendation(self, matches: List[MatchingResult], 
                                  entities: ExtractedEntities) -> Dict[str, Any]:
        """Generate overall recommendation based on matches and entity quality"""
        if not matches:
            return {
                "action": "no_suitable_loads",
                "message": "No suitable loads found for the trucker's requirements",
                "next_steps": ["Create lead for future opportunities", "Suggest alternative loads"]
            }
        
        best_match = matches[0]
        
        if best_match.recommendation == "auto_approve":
            return {
                "action": "auto_approve",
                "message": f"Excellent match found (Score: {best_match.overall_score:.1%})",
                "next_steps": ["Proceed with load assignment", "Confirm pricing"],
                "load_id": best_match.load_id
            }
        
        elif best_match.recommendation == "human_review":
            return {
                "action": "human_review",
                "message": f"Good match found but needs review (Score: {best_match.overall_score:.1%})",
                "next_steps": ["Route to human agent", "Review match details"],
                "load_id": best_match.load_id
            }
        
        else:
            return {
                "action": "create_lead",
                "message": f"Partial match found (Score: {best_match.overall_score:.1%})",
                "next_steps": ["Create lead in system", "Follow up when suitable loads available"],
                "load_id": best_match.load_id
            }

# Sample data for testing
def create_sample_loads() -> List[Load]:
    """Create sample loads based on the provided data"""
    sample_loads = [
        Load(
            id="load_001",
            booking_office="Surat Goods",
            message_id="29C7FB07FA60DB707DF544273C32813C",
            timestamp=datetime(2025, 8, 21, 16, 58, 18),
            from_location="Jigani",
            to_location="Nizampur",
            truck_type="Open truck",
            truck_length="6",
            tonnage="6",
            product="Ashirwad pipes",
            price=25000,
            num_trucks=4,
            eta="same day",
            status=LoadStatus.AVAILABLE
        ),
        Load(
            id="load_002",
            booking_office="Surat Goods",
            message_id="F782D14580618D32234A88816A01BD5E",
            timestamp=datetime(2025, 8, 22, 7, 11, 55),
            from_location="Jigani",
            to_location="Rangareddy",
            truck_type="Container",
            truck_length="20",
            tonnage="7",
            product="Ashirwad pipes",
            price=19000,
            num_trucks=1,
            eta="same day",
            status=LoadStatus.AVAILABLE
        ),
        Load(
            id="load_003",
            booking_office="Surat Goods",
            message_id="D1D21E014A7BB564F634E4DABDBF9281",
            timestamp=datetime(2025, 8, 25, 19, 29, 23),
            from_location="Attibele",
            to_location="Beed",
            truck_type="Container",
            truck_length="22",
            tonnage="8",
            product="Ashirwad pipes",
            price=22000,
            num_trucks=1,
            eta="same day",
            status=LoadStatus.AVAILABLE
        )
    ]
    return sample_loads

def create_sample_transcripts() -> List[Dict[str, Any]]:
    """Create sample transcripts from the provided data"""
    
    # Transcript 1: 8-ton, 19-feet open vehicle inquiry
    transcript_1 = {
        "id": "transcript_001",
        "caller_number": "8197852652",
        "duration": 180,
        "language": "mixed",
        "conversation": [
            {"speaker": "A", "text": "Hello.", "timestamp": 0},
            {"speaker": "B", "text": "Hello, Madam.", "timestamp": 1},
            {"speaker": "B", "text": "Ours is 8 tons, Madam. It's a wooden vehicle, 8 tons, Madam, 8 tons, 19 feet, 8 tons.", "timestamp": 45},
            {"speaker": "A", "text": "This is 4 tons, 19 feet, this is 4 tons.", "timestamp": 50},
            {"speaker": "B", "text": "Not a container, Madam. It's an open vehicle, we put a tarpaulin on top and close it.", "timestamp": 80}
        ]
    }
    
    return [transcript_1]

def test_system():
    """Test the complete system with sample data"""
    print("=" * 60)
    print("TRUCKING LOAD MATCHING SYSTEM - FULL TEST")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = TruckingMatchingOrchestrator()
    
    # Load sample data
    sample_loads = create_sample_loads()
    sample_transcripts = create_sample_transcripts()
    
    print(f"\nLoaded {len(sample_loads)} sample loads")
    print(f"Loaded {len(sample_transcripts)} sample transcripts")
    
    # Process transcript
    transcript_data = sample_transcripts[0]
    print(f"\n📞 Processing: {transcript_data['id']}")
    
    # Process transcript
    result = orchestrator.process_call_transcript(transcript_data, sample_loads)
    
    # Display results
    print(f"\n🚛 Extracted Entities:")
    entities = result['extracted_entities']
    print(f"   Truck Type: {entities.get('truck_type', 'Not specified')}")
    print(f"   Tonnage: {entities.get('tonnage', 'Not specified')} tons")
    print(f"   Length: {entities.get('truck_length', 'Not specified')} feet")
    
    print(f"\n📊 Matching Results:")
    print(f"   Loads Checked: {result['total_loads_checked']}")
    print(f"   Matches Found: {result['matches_found']}")
    
    if result['best_match']:
        best_match = result['best_match']
        print(f"\n🎯 Best Match:")
        print(f"   Load ID: {best_match['load_id']}")
        print(f"   Overall Score: {best_match['overall_score']:.1%}")
        print(f"   Recommendation: {best_match['recommendation'].title()}")
    
    print(f"\n🎯 Final Recommendation:")
    recommendation = result['recommendation']
    print(f"   Action: {recommendation['action'].upper()}")
    print(f"   Message: {recommendation['message']}")
    
    print(f"\n✅ System test completed successfully!")

if __name__ == "__main__":
    test_system()