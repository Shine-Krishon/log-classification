#!/usr/bin/env python3
"""
Test script to verify the Unicode logging and Pydantic validation fixes.
"""
import requests
import json
import tempfile
import csv
import os

def test_classification_endpoint():
    """Test the classification endpoint with sample data."""
    
    # Create a temporary CSV file with test data
    test_data = [
        {"source": "WebServer", "log_message": "User admin logged in successfully from IP 192.168.1.100"},
        {"source": "Database", "log_message": "Connection pool exhausted - unable to serve request"},
        {"source": "API", "log_message": "Endpoint /v1/users is deprecated, please use /v2/users instead"},
        {"source": "System", "log_message": "CPU usage exceeded 90% threshold - scaling required"},
        {"source": "Application", "log_message": "Payment processing completed for order #12345"}
    ]
    
    # Create temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['source', 'log_message'])
        writer.writeheader()
        writer.writerows(test_data)
        temp_csv_path = f.name
    
    try:
        print("🧪 Testing Enhanced Classification with Unicode Fix...")
        print(f"📄 Created test CSV: {temp_csv_path}")
        
        # Prepare the file for upload
        with open(temp_csv_path, 'rb') as f:
            files = {'file': ('test_logs.csv', f, 'text/csv')}
            
            # Make the classification request
            print("📡 Sending classification request...")
            response = requests.post(
                'http://localhost:8000/api/v1/classify/',
                files=files,
                timeout=120
            )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Classification completed without errors!")
            print(f"📈 Total logs processed: {result.get('total_logs', 'N/A')}")
            print(f"⏱️  Processing time: {result.get('processing_time_seconds', 'N/A'):.2f}s")
            
            # Check processing stats
            if 'processing_stats' in result:
                stats = result['processing_stats']
                print("\n📊 Processing Statistics:")
                print(f"   - Regex classified: {stats.get('regex_classified', 0)}")
                print(f"   - BERT classified: {stats.get('bert_classified', 0)}")
                print(f"   - LLM classified: {stats.get('llm_classified', 0)}")
                print(f"   - Unclassified: {stats.get('unclassified', 0)}")
            
            # Check classification results
            if 'classified_logs' in result:
                print("\n🎯 Classification Results:")
                for i, log_entry in enumerate(result['classified_logs'][:5]):  # Show first 5
                    print(f"   {i+1}. {log_entry['target_label']:<20} | {log_entry['source']:<10} | {log_entry['log_message'][:50]}...")
            
            return True
            
        else:
            print(f"❌ ERROR: Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_csv_path)
            print(f"🧹 Cleaned up temporary file: {temp_csv_path}")
        except:
            pass

def test_health_endpoint():
    """Test the health endpoint."""
    try:
        print("\n🏥 Testing Health Endpoint...")
        response = requests.get('http://localhost:8000/api/v1/health/', timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health endpoint working!")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Service: {result.get('service', 'unknown')}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health endpoint exception: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Fix Verification Tests...")
    print("=" * 60)
    
    # Test health first
    health_ok = test_health_endpoint()
    
    # Test classification
    classification_ok = test_classification_endpoint()
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY:")
    print(f"   Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   Classification: {'✅ PASS' if classification_ok else '❌ FAIL'}")
    
    if health_ok and classification_ok:
        print("\n🎉 ALL TESTS PASSED! Unicode and Pydantic fixes are working!")
        return True
    else:
        print("\n💥 SOME TESTS FAILED - Check the server logs for details")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)