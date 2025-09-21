#!/usr/bin/env python3
"""
Test script to verify the API response structure matches frontend expectations.
"""
import requests
import json
import io

def test_classification_response():
    """Test the classification endpoint and show the response structure."""
    
    # Create test CSV data
    csv_data = '''source,log_message
WebServer,ERROR: Database connection failed
Application,INFO: User login successful
System,WARNING: High memory usage detected'''

    print("🧪 Testing Classification API Response Structure...")
    print("=" * 50)
    
    try:
        # Test the classification endpoint
        files = {'file': ('test.csv', io.StringIO(csv_data), 'text/csv')}
        response = requests.post('http://localhost:8000/api/v1/classify/', files=files)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Response Status: 200 OK")
            print("\n📊 Response Structure:")
            print("=" * 30)
            print(f"success: {data.get('success')}")
            print(f"message: {data.get('message')}")
            print(f"total_logs: {data.get('total_logs')}")
            print(f"processing_time_seconds: {data.get('processing_time_seconds')}")
            print(f"output_file: {data.get('output_file')}")
            
            print("\n📈 Classification Stats:")
            print("=" * 25)
            class_stats = data.get('classification_stats', {})
            print(f"total_logs: {class_stats.get('total_logs')}")
            print(f"label_counts: {class_stats.get('label_counts')}")
            print(f"label_percentages: {class_stats.get('label_percentages')}")
            
            print("\n⚙️ Processing Stats:")
            print("=" * 20)
            proc_stats = data.get('processing_stats', {})
            print(f"regex_classified: {proc_stats.get('regex_classified')}")
            print(f"bert_classified: {proc_stats.get('bert_classified')}")
            print(f"llm_classified: {proc_stats.get('llm_classified')}")
            print(f"unclassified: {proc_stats.get('unclassified')}")
            
            print("\n🎯 Frontend Access Paths:")
            print("=" * 27)
            print(f"data.total_logs = {data.get('total_logs')}")
            print(f"data.processing_time_seconds = {data.get('processing_time_seconds')}")
            print(f"data.classification_stats.total_logs = {class_stats.get('total_logs')}")
            print(f"data.classification_stats.label_counts = {class_stats.get('label_counts')}")
            
            # Test if the structure matches what the frontend expects
            frontend_requirements = [
                ("data.total_logs", data.get('total_logs') is not None),
                ("data.processing_time_seconds", data.get('processing_time_seconds') is not None),
                ("data.classification_stats", data.get('classification_stats') is not None),
                ("data.classification_stats.label_counts", class_stats.get('label_counts') is not None)
            ]
            
            print("\n✅ Frontend Compatibility Check:")
            print("=" * 35)
            all_good = True
            for path, exists in frontend_requirements:
                status = "✅" if exists else "❌"
                print(f"{status} {path}: {'Available' if exists else 'Missing'}")
                if not exists:
                    all_good = False
            
            if all_good:
                print("\n🎉 SUCCESS: API response structure is compatible with frontend!")
            else:
                print("\n⚠️ WARNING: Some required fields are missing!")
                
        else:
            print(f"❌ Response Status: {response.status_code}")
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test Error: {e}")

if __name__ == "__main__":
    test_classification_response()