#!/usr/bin/env python3
"""Direct test of processor_bert_enhanced classification"""

from processor_bert_enhanced import classify_with_bert, get_model_info
import sys

# Test basic classification
test_message = "User 12345 logged in"

print("=== TESTING PROCESSOR_BERT_ENHANCED DIRECTLY ===")
print(f"Test message: '{test_message}'")

try:
    # Get model info first
    model_info = get_model_info()
    print(f"\nModel info: {model_info}")
    
    # Test classification
    result = classify_with_bert(test_message)
    print(f"\nClassification result: {result}")
    print(f"Result type: {type(result)}")
    
    # Test a few more cases
    test_cases = [
        "Failed login attempt detected",
        "User accessed dashboard",
        "Security alert: suspicious activity"
    ]
    
    print("\n=== ADDITIONAL TEST CASES ===")
    for msg in test_cases:
        try:
            result = classify_with_bert(msg)
            print(f"'{msg}' → {result}")
        except Exception as e:
            print(f"ERROR on '{msg}': {e}")
            
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()