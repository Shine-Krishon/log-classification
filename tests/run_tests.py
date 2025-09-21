#!/usr/bin/env python3
"""
Test suite runner for the log classification system.
"""
import os
import time
import requests
from pathlib import Path

# Test data directory
TEST_DATA_DIR = Path("tests/test_data")
API_BASE_URL = "http://localhost:8000"

def test_file_upload(filename):
    """Test uploading a specific test file."""
    filepath = TEST_DATA_DIR / filename
    
    if not filepath.exists():
        print(f"❌ Test file not found: {filepath}")
        return False
    
    print(f"🧪 Testing: {filename}")
    print(f"   File size: {filepath.stat().st_size / 1024:.1f} KB")
    
    try:
        with open(filepath, 'rb') as f:
            files = {'file': (filename, f, 'text/csv')}
            
            start_time = time.time()
            response = requests.post(f"{API_BASE_URL}/classify/", files=files, timeout=120)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                total_records = len(result.get('results', []))
                print(f"   ✅ Success: {total_records} records processed in {processing_time:.2f}s")
                print(f"   📊 Speed: {total_records/processing_time:.1f} records/second")
                
                # Show classification summary
                classifications = result.get('results', [])
                if classifications:
                    categories = {}
                    for record in classifications:
                        label = record.get('classification', 'unknown')
                        categories[label] = categories.get(label, 0) + 1
                    
                    print(f"   📈 Classification breakdown:")
                    for category, count in sorted(categories.items()):
                        percentage = (count / total_records) * 100
                        print(f"      {category}: {count} ({percentage:.1f}%)")
                
                return True
            else:
                print(f"   ❌ Failed: HTTP {response.status_code}")
                print(f"      Error: {response.text}")
                return False
                
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def run_test_suite():
    """Run the complete test suite."""
    print("🚀 Log Classification System - Test Suite")
    print("=" * 50)
    
    # Check if server is running
    health_endpoints = ["/health/", "/health", "/api/health/", "/api/health"]
    server_running = False
    
    for endpoint in health_endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                server_running = True
                break
        except:
            continue
    
    # If health endpoints don't work, try the root endpoint
    if not server_running:
        try:
            response = requests.get(f"{API_BASE_URL}/", timeout=5)
            if response.status_code == 200:
                server_running = True
        except:
            pass
    
    if not server_running:
        print("❌ Server is not running. Please start with: python main.py")
        return
    
    print("✅ Server is running and responding")
    print()
    
    # Test files in order of complexity
    test_files = [
        "small_test.csv",      # Quick validation
        "medium_test.csv",     # Standard testing
        "large_test.csv",      # Comprehensive testing
        "edge_cases_test.csv", # Error handling
        "stress_test.csv"      # Performance testing
    ]
    
    results = {}
    total_start_time = time.time()
    
    for filename in test_files:
        print(f"\n📝 Test {len(results) + 1}/{len(test_files)}")
        success = test_file_upload(filename)
        results[filename] = success
        
        if not success:
            print(f"   ⚠️  Consider investigating issues with {filename}")
        
        # Brief pause between tests
        time.sleep(1)
    
    total_end_time = time.time()
    total_time = total_end_time - total_start_time
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUITE SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    print(f"Total time: {total_time:.2f} seconds")
    print()
    
    print("Test Results:")
    for filename, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {filename}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your application is working perfectly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above for details.")
    
    print("\n💡 Tips:")
    print("   - Use small_test.csv for quick development testing")
    print("   - Use stress_test.csv for performance optimization")
    print("   - Use edge_cases_test.csv for robustness validation")
    print("   - Monitor system resources during large file processing")

if __name__ == "__main__":
    run_test_suite()