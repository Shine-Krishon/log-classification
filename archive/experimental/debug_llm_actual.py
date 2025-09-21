#!/usr/bin/env python3
"""
Test the actual LLM function with debugging
"""

import logging
from src.processors.processor_llm import classify_with_llm_batch

# Set up more verbose logging
logging.basicConfig(level=logging.INFO)

def test_actual_llm():
    print("🔍 Testing Actual LLM Function")
    print("=" * 50)
    
    # Test the problematic log
    test_logs = [
        ("LegacyCRM", "Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active")
    ]
    
    print("Test log:")
    print(f"  {test_logs[0]}")
    print()
    
    # Run actual LLM classification with debug output
    results = classify_with_llm_batch(test_logs)
    
    print(f"Result: {results}")
    
    expected = "workflow_error"
    actual = results[0] if results else "no_result"
    status = "✅" if actual == expected else "❌"
    print(f"{status} Expected: {expected}, Got: {actual}")

if __name__ == "__main__":
    test_actual_llm()