#!/usr/bin/env python3
"""
Quick test of the enhanced classification system
"""

from src.processors.processor_bert import classify_with_bert

def test_classifications():
    test_cases = [
        ("Failed login attempt for user admin from IP 192.168.1.100", "security_alert"),
        ("SQL injection attempt detected in user input", "security_alert"),
        ("User john.doe logged in successfully", "user_action"),
        ("Application started on port 8080", "system_notification"),
        ("Deprecated function xyz() called", "deprecation_warning"),
        ("Workflow failed due to timeout", "workflow_error")
    ]
    
    print("🔍 Testing Enhanced Classification System")
    print("=" * 50)
    
    for i, (msg, expected) in enumerate(test_cases, 1):
        result = classify_with_bert("test", msg)
        classification = result.get('classification', 'unknown')
        confidence = result.get('confidence', 0.0)
        
        status = "✅" if classification == expected else "❌"
        print(f"{i}. {status} \"{msg[:45]}{'...' if len(msg) > 45 else ''}\"")
        print(f"   -> {classification} (confidence: {confidence:.3f}) | Expected: {expected}")
        print()
    
    print("🎉 Enhanced Model Test Complete!")

if __name__ == "__main__":
    test_classifications()