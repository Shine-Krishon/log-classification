#!/usr/bin/env python3
"""
Test the enhanced classification fixes
"""

from src.services.enhanced_classification_service import EnhancedClassificationService

def test_enhanced_classification():
    print("🔍 Testing Enhanced Classification Service Fixes")
    print("=" * 50)
    
    # Create test data
    test_logs = [
        ("TestApp", "Failed login attempt for user admin from IP 192.168.1.100"),
        ("TestApp", "SQL injection attempt detected in user input"),
        ("TestApp", "User john.doe logged in successfully"),
        ("TestApp", "Application started on port 8080"),
        ("TestApp", "Deprecated function xyz() called"),
        ("TestApp", "Workflow failed due to timeout")
    ]
    
    # Initialize service
    service = EnhancedClassificationService()
    
    # Run classification
    results = service.classify_logs(test_logs, task_id="test-123")
    
    print(f"Input logs: {len(test_logs)}")
    print(f"Results: {len(results)}")
    print()
    
    # Display results
    for i, ((source, message), result) in enumerate(zip(test_logs, results), 1):
        print(f"{i}. \"{message[:50]}{'...' if len(message) > 50 else ''}\"")
        print(f"   -> {result}")
        print()
    
    # Display stats
    print("Classification Statistics:")
    stats = service.stats
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n🎉 Enhanced Classification Test Complete!")

if __name__ == "__main__":
    test_enhanced_classification()