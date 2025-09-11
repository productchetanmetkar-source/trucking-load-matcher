#!/usr/bin/env python3
"""
Quick test to check if the phone extraction method is working
"""

from agents.entity_extraction_agent import EntityExtractionAgent
from models.transcript_model import Transcript, ConversationTurn

def test_direct_phone_extraction():
    """Test the phone extraction method directly"""
    
    print("Testing direct phone extraction method:")
    print("=" * 40)
    
    # Test the actual agent
    agent = EntityExtractionAgent()
    
    # Test the _extract_phone_numbers method directly
    test_text = "trucker: 98... 9867... 33... 74... 13."
    result = agent._extract_phone_numbers(test_text)
    
    print(f"Input text: {test_text}")
    print(f"Direct phone extraction result: {result}")
    
    if result:
        print("✅ SUCCESS: Phone extraction method is working!")
    else:
        print("❌ FAILED: Phone extraction method is not working")
        
        # Debug further
        print("\nDebugging the method...")
        
        # Check if the method exists
        if hasattr(agent, '_extract_phone_numbers'):
            print("✅ Method exists")
        else:
            print("❌ Method does not exist")
            
        # Test with a simple number
        simple_result = agent._extract_phone_numbers("My number is 9876543210")
        print(f"Simple number test result: {simple_result}")

def test_full_entity_extraction():
    """Test the full entity extraction to see where it fails"""
    
    print("\n\nTesting full entity extraction:")
    print("=" * 40)
    
    agent = EntityExtractionAgent()
    
    transcript = Transcript(
        conversation_text="trucker: 98... 9867... 33... 74... 13.",
        turns=[ConversationTurn(speaker="trucker", text="98... 9867... 33... 74... 13.")]
    )
    
    # Extract entities
    entities = agent.extract_entities(transcript)
    
    print(f"Extracted phone number: {entities.fo_shared_number}")
    print(f"Regular phone field: {entities.phone_number}")
    print(f"Number exchanged flag: {entities.was_number_exchanged}")

if __name__ == "__main__":
    test_direct_phone_extraction()
    test_full_entity_extraction()