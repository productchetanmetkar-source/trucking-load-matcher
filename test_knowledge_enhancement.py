"""
Test Knowledge Base Enhancement
"""

from main import TruckingMatchingOrchestrator, create_sample_loads

def test_enhanced_system():
    print("Testing Knowledge Base Enhancement")
    print("=" * 50)
    
    # Test with industry terminology
    test_transcript = {
        "transcript_id": "KB_TEST",
        "conversation": "FO: Sir mujhe ek full body truck chahiye, 8 tonne ka\nBO: Route kya hai?\nFO: Bangaluru se Mumbai jana hai"
    }
    
    loads = create_sample_loads()
    orchestrator = TruckingMatchingOrchestrator()
    
    print(f"Test input: {test_transcript['conversation']}")
    print()
    
    try:
        result = orchestrator.process_call_transcript(test_transcript, loads)
        
        print("Extraction Results:")
        print(f"  Truck Type: {result['extracted_entities'].truck_type}")
        print(f"  Tonnage: {result['extracted_entities'].tonnage}")
        print(f"  Current Location: {result['extracted_entities'].current_location}")
        print(f"  Phone: {result['extracted_entities'].phone_number}")
        print()
        print("Expected Knowledge Base Improvements:")
        print("  - 'full body' should be recognized as container type")
        print("  - 'Bangaluru' should be normalized to 'Bangalore'")
        print("  - Industry terminology should be better understood")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_system()