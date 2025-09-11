#!/usr/bin/env python3
"""
Debug script to isolate the phone extraction issue
"""

import re
from typing import Optional

def debug_phone_extraction():
    """Debug phone extraction patterns step by step"""
    
    print("🔍 DEBUGGING PHONE EXTRACTION PATTERNS")
    print("=" * 50)
    
    # Test text from the failing case
    test_text = "shipper: Yes, tell me your number, your mobile number.\ntrucker: 98... 9867... 33... 74... 13."
    
    print(f"Test text: {test_text}")
    print()
    
    # Define all the patterns
    phone_pattern = re.compile(r'(?:\+91|91)?[6-9]\d{9}')
    fragmented_phone_pattern = re.compile(r'(\d{2,3})\.{2,3}(\d{3,4})\.{2,3}(\d{2,3})\.{2,3}(\d{2,3})\.{2,3}(\d{2,3})')
    number_sequence_pattern = re.compile(r'\b\d{2,4}\b')
    dot_pattern = re.compile(r'(\d{2,3})\.{2,}(\d{3,4})\.{2,}(\d{2,3})\.{2,}(\d{2,3})\.{2,}(\d{2,3})')
    
    # Test each pattern
    print("1. Testing standard phone pattern:")
    phone_matches = phone_pattern.findall(test_text)
    print(f"   Matches: {phone_matches}")
    
    print("\n2. Testing fragmented phone pattern:")
    fragmented_match = fragmented_phone_pattern.search(test_text)
    if fragmented_match:
        print(f"   Match found: {fragmented_match.groups()}")
        fragments = fragmented_match.groups()
        reconstructed = ''.join(fragments)
        print(f"   Reconstructed: {reconstructed}")
    else:
        print("   No match found")
    
    print("\n3. Testing number sequence pattern:")
    number_sequences = number_sequence_pattern.findall(test_text)
    print(f"   Sequences: {number_sequences}")
    
    print("\n4. Testing enhanced dot pattern:")
    dot_match = dot_pattern.search(test_text)
    if dot_match:
        print(f"   Match found: {dot_match.groups()}")
        fragments = dot_match.groups()
        reconstructed = ''.join(fragments)
        print(f"   Reconstructed: {reconstructed}")
    else:
        print("   No match found")
    
    print("\n5. Testing manual regex for the exact pattern:")
    # Test the exact pattern from the text: "98... 9867... 33... 74... 13."
    exact_pattern = re.compile(r'(\d+)\.{3}\s*(\d+)\.{3}\s*(\d+)\.{3}\s*(\d+)\.{3}\s*(\d+)')
    exact_match = exact_pattern.search(test_text)
    if exact_match:
        print(f"   Exact match found: {exact_match.groups()}")
        fragments = exact_match.groups()
        reconstructed = ''.join(fragments)
        print(f"   Reconstructed: {reconstructed}")
    else:
        print("   No exact match found")
    
    print("\n6. Testing simpler approach - find all digit groups:")
    digit_groups = re.findall(r'\d+', test_text)
    print(f"   All digits: {digit_groups}")
    
    # Filter to likely phone number candidates
    phone_candidates = [d for d in digit_groups if len(d) >= 2 and d[0] in '6789']
    print(f"   Phone candidates: {phone_candidates}")
    
    if len(phone_candidates) >= 3:
        potential_number = ''.join(phone_candidates)
        print(f"   Potential number: {potential_number}")
        if len(potential_number) >= 10:
            final_number = potential_number[:10]
            print(f"   Final number (10 digits): {final_number}")

def enhanced_phone_extraction(full_text: str) -> Optional[str]:
    """Working phone extraction function"""
    
    # Try standard phone pattern first
    phone_pattern = re.compile(r'(?:\+91|91)?[6-9]\d{9}')
    phone_matches = phone_pattern.findall(full_text)
    if phone_matches:
        return phone_matches[0]
    
    # Enhanced approach: Find all digit sequences and try to reconstruct
    digit_groups = re.findall(r'\d+', full_text)
    
    # Filter to groups that could be part of a phone number
    phone_digit_groups = []
    for group in digit_groups:
        if len(group) >= 2:  # At least 2 digits
            phone_digit_groups.append(group)
    
    # Try to reconstruct phone number
    if len(phone_digit_groups) >= 3:
        potential_number = ''.join(phone_digit_groups)
        
        # Look for a 10-digit sequence starting with 6,7,8,9
        for i in range(len(potential_number) - 9):
            candidate = potential_number[i:i+10]
            if candidate[0] in '6789' and len(candidate) == 10:
                return candidate
    
    return None

def test_enhanced_extraction():
    """Test the enhanced extraction function"""
    
    print("\n🧪 TESTING ENHANCED EXTRACTION FUNCTION")
    print("=" * 50)
    
    test_cases = [
        "98... 9867... 33... 74... 13.",
        "My number is 9876543210",
        "Call me on +91-9876543210",
        "98 76 54 32 10 is my number",
        "Sir, my mobile number is 98... 1234... 56... 78... 90, call me anytime"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        result = enhanced_phone_extraction(test_case)
        print(f"{i}. Input: {test_case}")
        print(f"   Result: {result}")
        print()

if __name__ == "__main__":
    debug_phone_extraction()
    test_enhanced_extraction()