import requests
import json
import time

def test_medium_dataset():
    """Test the enhanced 20K model on medium_test.csv dataset."""
    url = "http://localhost:8000/classify/"
    
    print("=== TESTING ENHANCED 20K MODEL ON MEDIUM DATASET ===")
    print("Dataset: medium_test.csv (110 log entries)")
    print("Expected: ModernHR-like cases and various other complex logs")
    print("-" * 70)
    
    start_time = time.time()
    
    try:
        # Upload and classify the medium test file
        with open("medium_test.csv", "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error Response: {response.text}")
            return
        
        result = response.json()
        
        # Summary Statistics
        print(f"✅ Classification completed successfully!")
        print(f"📊 Total processed: {result.get('total_processed', 'N/A')} logs")
        print(f"⏱️  Total processing time: {result.get('processing_time_seconds', 'N/A')} seconds")
        print(f"🚀 Our request time: {total_time:.2f} seconds")
        print()
        
        # Processor Statistics
        if 'statistics' in result:
            stats = result['statistics']
            print("🔧 PROCESSOR USAGE:")
            total_processed = sum(stats.values()) if stats else 0
            for processor, count in stats.items():
                percentage = (count / total_processed * 100) if total_processed > 0 else 0
                print(f"   {processor}: {count} ({percentage:.1f}%)")
            print()
        
        # Classification Distribution
        if 'classifications' in result:
            classifications = result['classifications']
            
            # Count classifications by label
            label_counts = {}
            processor_usage = {}
            
            for item in classifications:
                label = item.get('predicted_label', 'unknown')
                processor = item.get('processor_used', 'unknown')
                
                label_counts[label] = label_counts.get(label, 0) + 1
                processor_usage[processor] = processor_usage.get(processor, 0) + 1
            
            print("📋 CLASSIFICATION RESULTS:")
            for label, count in sorted(label_counts.items()):
                percentage = (count / len(classifications) * 100) if classifications else 0
                print(f"   {label}: {count} ({percentage:.1f}%)")
            print()
            
            # Look for ModernCRM entries specifically 
            modern_crm_entries = [item for item in classifications if 'ModernCRM' in item.get('source', '')]
            if modern_crm_entries:
                print("🎯 MODERN CRM CLASSIFICATIONS (ModernHR-like cases):")
                for i, item in enumerate(modern_crm_entries[:10], 1):  # Show first 10
                    log_msg = item.get('log_message', '')
                    if len(log_msg) > 50:
                        log_msg = log_msg[:50] + "..."
                    print(f"   {i}. {log_msg}")
                    print(f"      -> {item.get('predicted_label', 'N/A')} (via {item.get('processor_used', 'N/A')})")
                
                if len(modern_crm_entries) > 10:
                    print(f"   ... and {len(modern_crm_entries) - 10} more ModernCRM entries")
                print()
        
        # Performance Summary
        processing_time = result.get('processing_time_seconds', 0)
        total_logs = result.get('total_processed', 0)
        if processing_time > 0 and total_logs > 0:
            logs_per_second = total_logs / processing_time
            print(f"⚡ Performance: {logs_per_second:.1f} logs/second")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return None

if __name__ == "__main__":
    result = test_medium_dataset()
    if result:
        print("\n✅ Medium dataset test completed successfully!")
    else:
        print("\n❌ Medium dataset test failed!")