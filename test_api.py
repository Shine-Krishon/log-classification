import requests
import json

# Test the classification API with the updated 5K dataset model
def test_classification():
    url = "http://localhost:8000/classify/"
    
    # Open the test file
    with open("test_5k_model.csv", "rb") as f:
        files = {"file": f}
        
        try:
            response = requests.post(url, files=files)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Error Response: {response.text}")
                return
                
            result = response.json()
            print("\n=== CLASSIFICATION RESULTS WITH 5K DATASET MODEL ===")
            print(f"Total processed: {result.get('total_processed', 'N/A')}")
            print(f"Processing time: {result.get('processing_time_seconds', 'N/A')} seconds")
            
            # Show individual classifications
            if 'classifications' in result:
                print("\nIndividual Classifications:")
                for i, classification in enumerate(result['classifications'], 1):
                    log_msg = classification.get('log_message', 'N/A')
                    if len(log_msg) > 50:
                        log_msg = log_msg[:50] + "..."
                    print(f"{i}. {classification.get('source', 'N/A')}: {log_msg}")
                    print(f"   -> {classification.get('predicted_label', 'N/A')} (via {classification.get('processor_used', 'N/A')})")
                    print()
                    
            # Show model statistics  
            if 'statistics' in result:
                stats = result['statistics']
                print(f"Model Statistics:")
                for processor, count in stats.items():
                    print(f"  {processor}: {count} classifications")
                    
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_classification()