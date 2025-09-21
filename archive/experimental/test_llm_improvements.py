#!/usr/bin/env python3
"""
Test the improved LLM classification
"""

from src.processors.processor_llm import classify_with_llm_batch

def test_llm_improvements():
    print("🔍 Testing LLM Classification Improvements")
    print("=" * 50)
    
    # Test the problematic log that was unclassified
    test_logs = [
        ("LegacyCRM", "Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active"),
        ("TestApp", "SQL injection attempt detected in user input"),
        ("TestApp", "User john.doe logged in successfully")
    ]
    
    print("Test logs:")
    for i, (source, message) in enumerate(test_logs, 1):
        print(f"{i}. [{source}] {message}")
    print()
    
    # Run LLM classification
    results = classify_with_llm_batch(test_logs)
    
    print("LLM Results:")
    for i, ((source, message), result) in enumerate(zip(test_logs, results), 1):
        print(f"{i}. {result}")
        expected = {
            1: "workflow_error",  # Case escalation failed
            2: "security_alert",  # SQL injection
            3: "user_action"      # User login
        }
        status = "✅" if result == expected[i] else "❌"
        print(f"   {status} Expected: {expected[i]}, Got: {result}")
    print()
    
    print("🎉 LLM Improvement Test Complete!")

if __name__ == "__main__":
    test_llm_improvements()