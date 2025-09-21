#!/usr/bin/env python3
"""
Test the improved LLM classification with cache busting
"""

import time
from src.processors.processor_llm import classify_with_llm_batch

def test_llm_with_cache_busting():
    print("🔍 Testing LLM Classification Improvements (Fresh)")
    print("=" * 50)
    
    # Test logs with timestamp to avoid cache
    timestamp = int(time.time())
    test_logs = [
        ("LegacyCRM", f"Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active (test {timestamp})"),
        ("TestApp", f"SQL injection attempt detected in user input (test {timestamp})"),
        ("TestApp", f"User john.doe logged in successfully (test {timestamp})")
    ]
    
    print("Test logs:")
    for i, (source, message) in enumerate(test_logs, 1):
        print(f"{i}. [{source}] {message[:60]}...")
    print()
    
    # Run LLM classification
    results = classify_with_llm_batch(test_logs)
    
    print("LLM Results:")
    expected = ["workflow_error", "security_alert", "user_action"]
    
    for i, ((source, message), result, exp) in enumerate(zip(test_logs, results, expected), 1):
        status = "✅" if result == exp else "❌"
        print(f"{i}. {status} Expected: {exp}, Got: {result}")
    print()
    
    success_count = sum(1 for r, e in zip(results, expected) if r == e)
    print(f"Success Rate: {success_count}/{len(expected)} ({success_count/len(expected)*100:.1f}%)")
    print("🎉 LLM Improvement Test Complete!")

if __name__ == "__main__":
    test_llm_with_cache_busting()