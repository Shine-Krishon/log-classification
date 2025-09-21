"""
API testing script for the log classification service.
"""
import requests
import json
import pandas as pd
from io import StringIO
import time

# API base URL
BASE_URL = "http://127.0.0.1:8000"

def test_health_endpoint():
    """Test the health check endpoint."""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_root_endpoint():
    """Test the root welcome page."""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type')}")
        print(f"Content length: {len(response.text)} characters")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def create_test_csv():
    """Create a test CSV file for classification."""
    test_data = [
        ("WebApp", "User john.doe logged in successfully"),
        ("API", "GET /users/123 returned 200 OK"),
        ("LegacyCRM", "ERROR: Database connection timeout after 30 seconds"),
        ("WebApp", "User jane.smith logged out"),
        ("API", "POST /orders created new order #12345"),
        ("Database", "Connection pool exhausted, waiting for available connection"),
        ("LegacyCRM", "WARNING: Feature XYZ is deprecated and will be removed"),
        ("WebApp", "Failed login attempt for user admin"),
        ("API", "Rate limit exceeded for IP 192.168.1.100"),
        ("System", "Scheduled backup completed successfully")
    ]
    
    df = pd.DataFrame(test_data, columns=["source", "log_message"])
    csv_content = df.to_csv(index=False)
    
    print(f"📝 Created test CSV with {len(test_data)} log entries:")
    print(csv_content)
    
    return csv_content

def test_classify_endpoint():
    """Test the classification endpoint with valid data."""
    print("\n🔍 Testing classification endpoint...")
    
    # Create test CSV
    csv_content = create_test_csv()
    
    try:
        # Prepare file upload
        files = {
            'file': ('test_logs.csv', csv_content, 'text/csv')
        }
        
        print("📤 Uploading test CSV for classification...")
        start_time = time.time()
        
        # Test the new API endpoint with JSON response
        response = requests.post(f"{BASE_URL}/api/v1/classify/", files=files)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"Status: {response.status_code}")
        print(f"Processing time: {processing_time:.2f} seconds")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            # Parse the JSON response
            result = response.json()
            print(f"\n📊 Classification Results:")
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            print(f"Total logs: {result.get('total_logs')}")
            print(f"Processing time: {result.get('processing_time_seconds')}s")
            
            # Show classification stats
            if 'classification_stats' in result:
                stats = result['classification_stats']
                print(f"\n📈 Label Distribution:")
                for label, count in stats.get('label_counts', {}).items():
                    percentage = stats.get('label_percentages', {}).get(label, 0)
                    print(f"  {label}: {count} ({percentage}%)")
            
            # Show processing stats
            if 'processing_stats' in result:
                pstats = result['processing_stats']
                print(f"\n⚙️ Processing Statistics:")
                print(f"  Regex classified: {pstats.get('regex_classified', 0)}")
                print(f"  BERT classified: {pstats.get('bert_classified', 0)}")
                print(f"  LLM classified: {pstats.get('llm_classified', 0)}")
                print(f"  Unclassified: {pstats.get('unclassified', 0)}")
            
            return True
        else:
            print(f"❌ Classification failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Classification test failed: {e}")
        return False

def test_invalid_file_upload():
    """Test error handling with invalid files."""
    print("\n🔍 Testing invalid file upload handling...")
    
    test_cases = [
        # Empty file
        {
            'name': 'empty_file.csv',
            'content': '',
            'description': 'Empty file'
        },
        # Invalid CSV format
        {
            'name': 'invalid.csv',
            'content': 'not,a,valid\ncsv,format,here,extra',
            'description': 'Invalid CSV format'
        },
        # Missing required columns
        {
            'name': 'missing_columns.csv',
            'content': 'wrong,columns\nvalue1,value2',
            'description': 'Missing required columns'
        },
        # Non-CSV file
        {
            'name': 'test.txt',
            'content': 'This is not a CSV file',
            'description': 'Wrong file type'
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n  Testing: {test_case['description']}")
        
        try:
            files = {
                'file': (test_case['name'], test_case['content'], 'text/plain')
            }
            
            response = requests.post(f"{BASE_URL}/api/v1/classify/", files=files)
            
            print(f"    Status: {response.status_code}")
            print(f"    Response: {response.text[:100]}...")
            
            # Should return 400 for all these cases
            results.append(response.status_code == 400)
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            results.append(False)
    
    return all(results)

def test_file_validation_endpoint():
    """Test the file validation endpoint."""
    print("\n🔍 Testing file validation endpoint...")
    
    # Create test CSV
    csv_content = create_test_csv()
    
    try:
        files = {
            'file': ('test_logs.csv', csv_content, 'text/csv')
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/validate/", files=files)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Validation Results:")
            print(f"  Valid: {result.get('is_valid')}")
            print(f"  Filename: {result.get('filename')}")
            print(f"  File size: {result.get('file_size_mb')} MB")
            print(f"  Rows: {result.get('rows_count')}")
            print(f"  Columns: {result.get('columns')}")
            print(f"  Errors: {result.get('validation_errors')}")
            
            return result.get('is_valid', False)
        else:
            print(f"❌ Validation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def test_download_endpoint():
    """Test the download endpoint (backward compatibility)."""
    print("\n🔍 Testing download endpoint...")
    
    # Create test CSV
    csv_content = create_test_csv()
    
    try:
        files = {
            'file': ('test_logs.csv', csv_content, 'text/csv')
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/classify/download/", files=files)
        
        print(f"Status: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            # Parse the returned CSV
            result_df = pd.read_csv(StringIO(response.text))
            print(f"✅ Download successful:")
            print(f"  Total logs: {len(result_df)}")
            print(f"  Columns: {list(result_df.columns)}")
            
            if 'target_label' in result_df.columns:
                label_counts = result_df['target_label'].value_counts()
                print(f"  Labels: {dict(label_counts)}")
            
            return True
        else:
            print(f"❌ Download failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Download test failed: {e}")
        return False

def test_large_file_handling():
    """Test handling of large files."""
    print("\n🔍 Testing large file handling...")
    
    # Create a large CSV (simulate file size limit testing)
    large_data = []
    for i in range(1000):  # Create 1000 log entries
        large_data.append((f"Source{i%10}", f"Log message number {i} with some content"))
    
    df = pd.DataFrame(large_data, columns=["source", "log_message"])
    csv_content = df.to_csv(index=False)
    
    print(f"📊 Testing with {len(large_data)} log entries ({len(csv_content)/1024:.1f} KB)")
    
    try:
        files = {
            'file': ('large_test.csv', csv_content, 'text/csv')
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/v1/classify/", files=files)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        print(f"Status: {response.status_code}")
        print(f"Processing time: {processing_time:.2f} seconds")
        print(f"Throughput: {len(large_data)/processing_time:.1f} logs/second")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully processed {result.get('total_logs')} logs")
            
            # Show processing stats for large file
            if 'processing_stats' in result:
                pstats = result['processing_stats']
                print(f"  Regex: {pstats.get('regex_classified', 0)}")
                print(f"  BERT: {pstats.get('bert_classified', 0)}")
                print(f"  LLM: {pstats.get('llm_classified', 0)}")
            
            return True
        else:
            print(f"❌ Large file processing failed: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Large file test failed: {e}")
        return False

def run_all_tests():
    """Run all API tests."""
    print("🚀 Starting comprehensive API testing...\n")
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Root Endpoint", test_root_endpoint),
        ("File Validation", test_file_validation_endpoint),
        ("Valid Classification", test_classify_endpoint),
        ("Download Endpoint", test_download_endpoint),
        ("Invalid File Handling", test_invalid_file_upload),
        ("Large File Processing", test_large_file_handling)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print('='*60)
        
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            results[test_name] = False
            print(f"\n❌ FAILED: {test_name} - {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print('='*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return results

if __name__ == "__main__":
    run_all_tests()