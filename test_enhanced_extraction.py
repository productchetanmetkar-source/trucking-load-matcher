"""
Test Enhanced Entity Extraction with Knowledge Base
"""

from agents.entity_extraction_agent import EntityExtractionAgent
from models.transcript_model import Transcript, ConversationTurn
import time

def test_knowledge_enhancement():
    print("Testing Enhanced Entity Extraction with Knowledge Base")
    print("=" * 60)
    
    # Test case with industry terminology
    transcript = Transcript(
        id="TEST_KNOWLEDGE",
        turns=[
            ConversationTurn(
                speaker="FO",
                text="Sir mujhe ek full body truck chahiye, 8 tonne ka, Bangaluru se Mumbai jana hai",
                timestamp=time.time()  # Use timestamp as float instead of datetime
            )
        ],
        caller_phone="+91-9876543210",
        duration_minutes=1,
        booking_office="BO_Test"
    )
    
    agent = EntityExtractionAgent()
    
    print("Input text: 'Sir mujhe ek full body truck chahiye, 8 tonne ka, Bangaluru se Mumbai jana hai'")
    print()
    
    # Test original method
    print("1. ORIGINAL EXTRACTION:")
    original_entities = agent.extract_entities(transcript)
    print(f"   Truck Type: {original_entities.truck_type}")
    print(f"   Route From: {original_entities.route_from}")
    print(f"   Route To: {original_entities.route_to}")
    print()
    
    # Test enhanced method
    print("2. ENHANCED EXTRACTION WITH KNOWLEDGE BASE:")
    try:
        enhanced_entities = agent.extract_entities_with_knowledge(transcript)
        print(f"   Truck Type: {enhanced_entities.truck_type} (should normalize 'full body' to 'container')")
        print(f"   Route From: {enhanced_entities.route_from} (should normalize 'Bangaluru' to 'Bangalore')")
        print(f"   Route To: {enhanced_entities.route_to}")
        print(f"   Tonnage: {enhanced_entities.tonnage}")
        print("   ✅ Knowledge base integration working!")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   Check your code integration")

if __name__ == "__main__":
    test_knowledge_enhancement()