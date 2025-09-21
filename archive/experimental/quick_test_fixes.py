#!/usr/bin/env python3
"""
Quick test script to verify all the fixes are working.
"""
import requests
import json

def test_health_endpoint():
    """Test the health endpoint."""
    try:
        print("[HEALTH] Testing health endpoint...")
        response = requests.get('http://localhost:8000/api/v1/health/', timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"[SUCCESS] Health endpoint working!")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Service: {result.get('service', 'unknown')}")
            print(f"   Enhanced Model: {result.get('components', {}).get('enhanced_bert_20k', 'unknown')}")
            print(f"   Model Info: {result.get('components', {}).get('enhanced_model_info', 'unknown')}")
            return True
        else:
            print(f"[ERROR] Health endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Health endpoint exception: {str(e)}")
        return False

def test_classification_quick():
    """Quick classification test."""
    try:
        print("\n[CLASSIFY] Testing classification endpoint...")
        
        # Simple test data
        import tempfile
        import csv
        
        test_data = [
            {"source": "WebServer", "log_message": "User login failed for admin"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['source', 'log_message'])
            writer.writeheader()
            writer.writerows(test_data)
            temp_csv_path = f.name
        
        with open(temp_csv_path, 'rb') as f:
            files = {'file': ('test.csv', f, 'text/csv')}
            response = requests.post('http://localhost:8000/api/v1/classify/', files=files, timeout=30)
        
        if response.status_code == 200:
            print("[SUCCESS] Classification working!")
            result = response.json()
            print(f"   Total logs: {result.get('total_logs', 'N/A')}")
            print(f"   Processing time: {result.get('processing_time_seconds', 'N/A'):.3f}s")
            return True
        else:
            print(f"[ERROR] Classification failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Classification exception: {str(e)}")
        return False

def main():
    """Run quick tests."""
    print("🔧 Quick Fix Verification Test")
    print("=" * 40)
    
    health_ok = test_health_endpoint()
    classify_ok = test_classification_quick()
    
    print("\n" + "=" * 40)
    print("📋 QUICK TEST SUMMARY:")
    print(f"   Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   Classification: {'✅ PASS' if classify_ok else '❌ FAIL'}")
    
    if health_ok and classify_ok:
        print("\n🎉 ALL FIXES VERIFIED! System is working properly!")
    else:
        print("\n💥 Some issues remain - check the logs")

if __name__ == "__main__":
    main()