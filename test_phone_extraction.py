#!/usr/bin/env python3
"""
Test the corrected phone extraction
"""

import re
from typing import Optional

def corrected_phone_extraction(full_text: str) -> Optional[str]:
    """Corrected phone extraction that properly handles the fragmented format"""
    
    # Try standard phone pattern first
    phone_pattern = re.compile(r'(?:\+91|91)?[6-9]\d{9}')
    phone_matches = phone_pattern.findall(full_text)
    if phone_matches:
        return phone_matches[0]
    
    # Try the exact pattern for fragmented numbers like "98... 9867... 33... 74... 13"
    exact_pattern = re.compile(r'(\d+)\.{3}\s*(\d+)\.{3}\s*(\d+)\.{3}\s*(\d+)\.{3}\s*(\d+)')
    exact_match = exact_pattern.search(full_text)
    if exact_match:
        fragments = exact_match.groups()
        print(f"Debug: Found fragments: {fragments}")
        
        # The correct reconstruction for "98... 9867... 33... 74... 13" should be:
        # 98 + 96 (first 2 of 9867) + 67 (last 2 of 9867) + 33 + 74 + 13 = 9896673341
        # OR simply: 98 + 9867 but take only 2 digits + 33 + 74 + 13 = 9896733741
        
        # Let me try the simpler approach: just concatenate and take first 10
        reconstructed = ''.join(fragments)
        print(f"Debug: Reconstructed: {reconstructed}")
        
        if len(reconstructed) >= 10 and reconstructed[0] in '6789':
            final_number = reconstructed[:10]
            print(f"Debug: Final number: {final_number}")
            return final_number
    
    # Fallback: Enhanced approach using all digit sequences
    digit_groups = re.findall(r'\d+', full_text)
    print(f"Debug: All digit groups: {digit_groups}")
    
    # Filter to groups that could be part of a phone number
    phone_digit_groups = [group for group in digit_groups if len(group) >= 2]
    print(f"Debug: Phone digit groups: {phone_digit_groups}")
    
    if len(phone_digit_groups) >= 3:
        potential_number = ''.join(phone_digit_groups)
        print(f"Debug: Potential number: {potential_number}")
        
        if len(potential_number) >= 10 and potential_number[0] in '6789':
            return potential_number[:10]
    
    return None

def test_corrected_extraction():
    """Test the corrected phone extraction"""
    
    print("Testing corrected phone extraction:")
    print("=" * 40)
    
    test_case = "trucker: 98... 9867... 33... 74... 13."
    expected = "9896733741"  # This should be the correct number
    
    print(f"Input: {test_case}")
    print(f"Expected: {expected}")
    
    result = corrected_phone_extraction(test_case)
    print(f"Result: {result}")
    
    if result == expected:
        print("✅ SUCCESS!")
    else:
        print("❌ Still not matching expected result")
        
        # Let's manually verify what the correct number should be
        print("\nManual verification:")
        print("Fragments: 98, 9867, 33, 74, 13")
        print("Concatenated: 989867337413")
        print("First 10: 9898673374")
        print("But expected: 9896733741")
        print("There's a discrepancy in the expected vs actual reconstruction!")

if __name__ == "__main__":
    test_corrected_extraction()