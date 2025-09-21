#!/usr/bin/env python3
"""Debug the API response structure"""

import requests
import json

csv_file_path = "api_test.csv"

print("=== DEBUGGING API RESPONSE ===")

try:
    with open(csv_file_path, 'rb') as f:
        files = {'file': ('api_test.csv', f, 'text/csv')}
        response = requests.post(
            "http://localhost:8000/api/v1/classify/",
            files=files,
            timeout=30
        )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nFull Response Structure:")
        print(json.dumps(result, indent=2, default=str))
        
        # Check what keys are available
        print(f"\nResponse Keys: {list(result.keys())}")
        
        # Check if there are different field names
        for key in result.keys():
            value = result[key]
            if isinstance(value, list) and value:
                print(f"\nKey '{key}' contains {len(value)} items:")
                if len(value) > 0:
                    print(f"First item structure: {type(value[0])}")
                    if isinstance(value[0], dict):
                        print(f"First item keys: {list(value[0].keys())}")
                        print(f"First item: {value[0]}")
    else:
        print(f"Error Response: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()