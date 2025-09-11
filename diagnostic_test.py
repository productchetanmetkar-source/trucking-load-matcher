#!/usr/bin/env python3
"""
Diagnostic test to see what's happening in the conversation parsing
"""

from agents.entity_extraction_agent import EntityExtractionAgent
from models.transcript_model import Transcript, ConversationTurn

def diagnostic_test():
    """Run a detailed diagnostic of the entity extraction process"""
    
    print("🔍 DIAGNOSTIC TEST - Entity Extraction Flow")
    print("=" * 50)
    
    agent = EntityExtractionAgent()
    
    # Create the same transcript from the failing test
    transcript = Transcript(
        conversation_text="shipper: Yes, tell me your number, your mobile number.\ntrucker: 98... 9867... 33... 74... 13.",
        turns=[
            ConversationTurn(speaker="shipper", text="Yes, tell me your number, your mobile number."),
            ConversationTurn(speaker="trucker", text="98... 9867... 33... 74... 13.")
        ]
    )
    
    print("1. Testing conversation parsing:")
    print("-" * 30)
    
    # Test the _parse_conversation method
    conversation_data = agent._parse_conversation(transcript)
    
    print(f"Full text: {conversation_data['full_text']}")
    print(f"Total turns: {len(conversation_data['turns'])}")
    print(f"FO turns: {len(conversation_data['fo_turns'])}")
    print(f"Shipper turns: {len(conversation_data['shipper_turns'])}")
    print(f"TI turns: {len(conversation_data['ti_turns'])}")
    
    print("\nTurn details:")
    for i, turn in enumerate(conversation_data['turns']):
        print(f"  Turn {i+1}: {turn['speaker']} ({turn['speaker_type']}) -> {turn['text']}")
    
    print("\n2. Testing deterministic entity extraction:")
    print("-" * 30)
    
    deterministic = agent._extract_deterministic_entities(conversation_data)
    print("Deterministic entities:")
    for key, value in deterministic.items():
        print(f"  {key}: {value}")
    
    print("\n3. Testing conversational entity extraction:")
    print("-" * 30)
    
    conversational = agent._extract_conversational_entities(conversation_data)
    print("Conversational entities:")
    for key, value in conversational.items():
        print(f"  {key}: {value}")
    
    print("\n4. Testing phone extraction specifically:")
    print("-" * 30)
    
    phone_result = agent._extract_phone_numbers(conversation_data['full_text'])
    print(f"Phone extraction result: {phone_result}")
    
    print("\n5. Testing final entity building:")
    print("-" * 30)
    
    final_entities = agent._build_entities_object(deterministic, conversational)
    print(f"fo_shared_number: {final_entities.fo_shared_number}")
    print(f"phone_number: {final_entities.phone_number}")
    print(f"was_number_exchanged: {final_entities.was_number_exchanged}")
    
    print("\n6. Full extraction test:")
    print("-" * 30)
    
    complete_entities = agent.extract_entities(transcript)
    print(f"Complete fo_shared_number: {complete_entities.fo_shared_number}")
    print(f"Complete phone_number: {complete_entities.phone_number}")
    print(f"Complete was_number_exchanged: {complete_entities.was_number_exchanged}")

if __name__ == "__main__":
    diagnostic_test()