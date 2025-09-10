"""
Test Knowledge Base with Correct Format
"""

from main import TruckingMatchingOrchestrator, create_sample_loads

def test_knowledge_with_industry_terms():
    print("Testing Knowledge Base with Industry Terminology")
    print("=" * 60)
    
    # Create test transcript with correct format and industry terms
    test_transcript = {
        'id': 'KB_TEST_001',
        'caller_number': '9876543210',
        'duration': 120,
        'language': 'mixed',
        'conversation': [
            {
                'speaker': 'A',
                'text': 'Hello sir, mujhe ek full body truck chahiye',
                'timestamp': 0
            },
            {
                'speaker': 'B', 
                'text': 'Kitna tonnage chahiye?',
                'timestamp': 5
            },
            {
                'speaker': 'A',
                'text': '8 tonne ka chahiye, Bangaluru se Mumbai jana hai',
                'timestamp': 10
            },
            {
                'speaker': 'B',
                'text': 'Open truck nahi loge? Full body expensive hai',
                'timestamp': 15
            },
            {
                'speaker': 'A',
                'text': 'Nahi sir, full body hi chahiye. 19 feet length. Phone number 9876543210',
                'timestamp': 20
            }
        ]
    }
    
    loads = create_sample_loads()
    orchestrator = TruckingMatchingOrchestrator()
    
    print("Test conversation includes:")
    print("- 'full body truck' (should normalize to 'container')")
    print("- 'Bangaluru' (should normalize to 'Bangalore')")
    print("- Mixed Hindi/English terminology")
    print()
    
    try:
        result = orchestrator.process_call_transcript(test_transcript, loads)
        
    print("EXTRACTION RESULTS:")
    entities = result['extracted_entities']

    # Check if entities is a dictionary or object
    if isinstance(entities, dict):
        print(f"  Truck Type: {entities.get('truck_type')}")
        print(f"  Tonnage: {entities.get('tonnage')}")
        print(f"  Truck Length: {entities.get('truck_length')}")
        print(f"  Current Location: {entities.get('current_location')}")
        print(f"  Phone: {entities.get('phone_number')}")
        print(f"  Confidence: {entities.get('confidence_scores', {}).get('overall', 0):.2%}")
    else:
        # It's an object with attributes
        print(f"  Truck Type: {entities.truck_type}")
        print(f"  Tonnage: {entities.tonnage}")
        print(f"  Truck Length: {entities.truck_length}")
        print(f"  Current Location: {entities.current_location}")
        print(f"  Phone: {entities.phone_number}")
        print(f"  Confidence: {entities.confidence_scores.get('overall', 0):.2%}")

    print()

    print("KNOWLEDGE BASE IMPACT:")
    conversation_text = " ".join([turn['text'] for turn in test_transcript['conversation']])
    print(f"Raw text contains: {conversation_text}")

    if 'full body' in conversation_text.lower():
        truck_type = entities.get('truck_type') if isinstance(entities, dict) else entities.truck_type
        if truck_type == 'container':
            print("✅ 'full body' correctly normalized to 'container'")
        else:
            print(f"❌ 'full body' not normalized (got: {truck_type})")

    if 'bangaluru' in conversation_text.lower():
        location = entities.get('current_location') if isinstance(entities, dict) else entities.current_location
        if location == 'Bangalore':
            print("✅ 'Bangaluru' correctly normalized to 'Bangalore'")
        else:
            print(f"❌ 'Bangaluru' not normalized (got: {location})")
            print()
            print("MATCHING RESULTS:")
            print(f"  Matches Found: {len(result['matches'])}")
            if result['matches']:
                best_match = result['matches'][0]
                print(f"  Best Match Score: {best_match['score']:.1%}")
                print(f"  Recommendation: {result.get('recommendation', 'Unknown')}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_knowledge_with_industry_terms()