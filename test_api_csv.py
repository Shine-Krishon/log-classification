#!/usr/bin/env python3
"""Test the API endpoint with CSV file upload"""

import requests
import os

# Test the API with file upload
csv_file_path = "api_test.csv"

print("=== TESTING API WITH CSV FILE ===")

try:
    # Test file upload to classify endpoint
    with open(csv_file_path, 'rb') as f:
        files = {'file': ('api_test.csv', f, 'text/csv')}
        response = requests.post(
            "http://localhost:8000/api/v1/classify/",
            files=files,
            timeout=30
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Classification successful!")
        print(f"Processing details: {result.get('processing_details', {})}")
        
        # Show classifications
        classifications = result.get('classifications', [])
        print(f"\nClassifications ({len(classifications)} results):")
        
        expected_results = [
            ("User 12345 logged in", "user_action"),
            ("Failed login attempt from IP 192.168.1.100", "security_alert"),
            ("User accessed dashboard page", "user_action"),
            ("SQL injection attempt detected", "security_alert"),
            ("User uploaded file report.pdf", "user_action")
        ]
        
        correct_count = 0
        for i, (expected_msg, expected_cat) in enumerate(expected_results):
            if i < len(classifications):
                actual = classifications[i]
                actual_cat = actual.get('classification', 'unknown')
                confidence = actual.get('confidence', 0)
                
                is_correct = actual_cat == expected_cat
                correct_count += is_correct
                status = "✅" if is_correct else "❌"
                
                print(f"{status} '{expected_msg[:40]}...' → {actual_cat} (expected: {expected_cat}, conf: {confidence:.2f})")
            else:
                print(f"❌ Missing result for: {expected_msg}")
        
        accuracy = correct_count / len(expected_results) if expected_results else 0
        print(f"\nAPI Test Accuracy: {accuracy:.1%} ({correct_count}/{len(expected_results)})")
        
    else:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error testing API: {e}")

print("\n=== API TEST COMPLETE ===")