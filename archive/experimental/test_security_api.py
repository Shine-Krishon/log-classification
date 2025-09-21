#!/usr/bin/env python3
"""
Test the classification API with security-focused test data.
"""
import requests
import csv
import tempfile
import json

def test_security_classification_api():
    """Test the full API with security test cases."""
    
    print("🔒 Testing Full API with Security Classification Fixes")
    print("=" * 60)
    
    try:
        # Test with our security test file
        with open('security_test.csv', 'rb') as f:
            files = {'file': ('security_test.csv', f, 'text/csv')}
            
            print("📡 Sending classification request...")
            response = requests.post(
                'http://localhost:8000/api/v1/classify/',
                files=files,
                timeout=60
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Classification completed successfully!")
            
            print(f"\n📊 Processing Stats:")
            stats = result.get('processing_stats', {})
            print(f"   - Regex classified: {stats.get('regex_classified', 0)}")
            print(f"   - BERT classified: {stats.get('bert_classified', 0)}")
            print(f"   - LLM classified: {stats.get('llm_classified', 0)}")
            print(f"   - Unclassified: {stats.get('unclassified', 0)}")
            
            print(f"\n🎯 Classification Results:")
            security_correct = 0
            security_total = 0
            
            for log_entry in result.get('classified_logs', []):
                source = log_entry['source']
                message = log_entry['log_message']
                label = log_entry['target_label']
                
                # Check security classifications
                if 'escalation' in message.lower() or 'failed login' in message.lower() or 'blocked' in message.lower() or 'unauthorized' in message.lower():
                    security_total += 1
                    if label == 'system_notification':
                        security_correct += 1
                        status = "✅"
                    else:
                        status = "❌"
                    print(f"   {status} SECURITY: {label:<20} | {message[:50]}...")
                else:
                    print(f"   ✅ GENERAL: {label:<20} | {message[:50]}...")
            
            if security_total > 0:
                accuracy = (security_correct / security_total) * 100
                print(f"\n🎯 Security Classification Accuracy: {accuracy:.1f}% ({security_correct}/{security_total})")
                
                if accuracy >= 90:
                    print("🎉 Excellent security classification performance!")
                    return True
                else:
                    print("⚠️  Security classification needs improvement")
                    return False
            else:
                print("ℹ️  No security logs found in test")
                return True
                
        else:
            print(f"❌ Classification failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_security_classification_api()
    print(f"\n🏁 Test Result: {'SUCCESS' if success else 'FAILED'}")