#!/usr/bin/env python3
"""
Test script to verify improved security log classification.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.processors.processor_regex import classify_with_regex

def test_security_classifications():
    """Test security-related log classifications."""
    
    print("🔒 Testing Security Log Classification Improvements")
    print("=" * 60)
    
    # Test cases for security-related logs
    test_cases = [
        # Should be system_notification (security alerts)
        ("Security", "IP 192.168.133.114 blocked due to potential attack", "system_notification"),
        ("Security", "Admin access escalation detected for user 9429", "system_notification"),
        ("Security", "Failed login attempt from IP 10.0.0.1", "system_notification"),
        ("Security", "Unauthorized access attempt detected", "system_notification"),
        ("Security", "Suspicious activity from user account", "system_notification"),
        
        # Should still be user_action (legitimate user activities)
        ("App", "User 12345 logged in successfully", "user_action"),
        ("App", "User profile updated by john_doe", "user_action"),
        ("App", "File data.csv uploaded by user", "user_action"),
        
        # Should be workflow_error (actual system failures)
        ("System", "Database connection failed", "workflow_error"),
        ("System", "File processing aborted due to error", "workflow_error"),
        
        # Should be deprecation_warning
        ("API", "Feature will be retired in version 4.0", "deprecation_warning"),
        ("System", "Method no longer supported", "deprecation_warning"),
    ]
    
    passed = 0
    failed = 0
    
    for source, message, expected in test_cases:
        result = classify_with_regex(source, message)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
            
        print(f"{status} | {expected:<20} | {result:<20} | {message[:50]}...")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("❌ Some classifications need improvement")
        return False
    else:
        print("✅ All security classifications working correctly!")
        return True

if __name__ == "__main__":
    test_security_classifications()