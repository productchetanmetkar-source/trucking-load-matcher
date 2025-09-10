"""
Test Knowledge Base Integration
"""

from knowledge.trucking_knowledge import trucking_knowledge
import json

def test_knowledge_base():
    print("Testing Trucking Knowledge Base Integration...")
    print("=" * 50)
    
    # Test 1: Truck Classifications
    print("\n1. Testing Truck Classifications:")
    aliases = trucking_knowledge.get_truck_type_aliases("container")
    print(f"Container aliases: {aliases}")
    
    # Test 2: Location Normalization  
    print("\n2. Testing Location Normalization:")
    test_locations = ["bangaluru", "mumbay", "channai", "invalid_city"]
    for loc in test_locations:
        normalized = trucking_knowledge.normalize_location(loc)
        print(f"'{loc}' → '{normalized}'")
    
    # Test 3: Rate Estimation
    print("\n3. Testing Rate Estimation:")
    rate = trucking_knowledge.get_rate_estimate("container", 500, 1.2)
    if rate:
        print(f"Container 500km estimate: ₹{rate['estimated_rate']:,.0f}")
        print(f"Rate range: ₹{rate['rate_range']['min']:,.0f} - ₹{rate['rate_range']['max']:,.0f}")
    
    # Test 4: Knowledge Context Size
    print("\n4. Testing Knowledge Context:")
    context = trucking_knowledge.get_knowledge_context()
    context_str = json.dumps(context)
    print(f"Context size: {len(context_str):,} characters")
    print(f"Context keys: {list(context.keys())}")
    
    # Test 5: Truck Type Detection
    print("\n5. Testing Truck Type Detection:")
    test_texts = [
        "I need a full body truck",
        "20 foot container available",
        "open truck chahiye", 
        "semi-trailer required"
    ]
    
    for text in test_texts:
        found_type = None
        for truck_type, data in trucking_knowledge.truck_classifications.items():
            aliases = data.get('aliases', [])
            if any(alias.lower() in text.lower() for alias in aliases):
                found_type = truck_type
                break
        print(f"'{text}' → {found_type}")
    
    print("\n✅ Knowledge Base Test Complete!")

if __name__ == "__main__":
    test_knowledge_base()