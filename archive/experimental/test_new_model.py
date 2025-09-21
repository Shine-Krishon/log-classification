#!/usr/bin/env python3
"""
Test the newly trained security-enhanced model
"""

import joblib
import pandas as pd

def test_security_model():
    print("🧪 Testing Security-Enhanced Model")
    print("=" * 40)
    
    # Load the model
    try:
        model = joblib.load('log_classifier_with_security_alerts.joblib')
        print("✅ Model loaded successfully!")
        print(f"   Model type: {type(model)}")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return
    
    # Check dataset classes
    df = pd.read_csv('logs_chunk1.csv')
    classes = sorted(df['target_label'].unique())
    print(f"   Dataset classes ({len(classes)}): {classes}")
    
    # Test security alert detection
    print(f"\n🔒 Security Alert Detection Test:")
    
    security_tests = [
        "Failed login attempt for user admin from IP 192.168.1.100",
        "SQL injection attempt detected in user input",
        "Unauthorized access attempt detected from IP 10.0.0.5",
        "DDoS attack detected from multiple IP addresses",
        "Malicious file upload detected: virus signature found",
        "Brute force attack detected against user root",
        "Suspicious network traffic blocked by firewall"
    ]
    
    security_correct = 0
    for test_msg in security_tests:
        pred = model.predict([test_msg])[0]
        proba = max(model.predict_proba([test_msg])[0])
        
        is_correct = pred == 'security_alert'
        if is_correct:
            security_correct += 1
        
        status = "✅" if is_correct else "❌"
        print(f"  {status} \"{test_msg}\"")
        print(f"      -> {pred} (confidence: {proba:.3f})")
    
    security_accuracy = security_correct / len(security_tests)
    print(f"\n  Security Detection Accuracy: {security_accuracy:.1%} ({security_correct}/{len(security_tests)})")
    
    # Test non-security classification
    print(f"\n📝 Non-Security Classification Test:")
    
    other_tests = [
        ("User john.doe logged in successfully", "user_action"),
        ("Application started successfully on port 8080", "system_notification"),
        ("Database backup completed at 2025-09-14 02:00:00", "system_notification"),
        ("Payment processing failed: insufficient funds for order #12345", "workflow_error"),
        ("Configuration file config.yaml reloaded successfully", "system_notification"),
        ("API endpoint /metrics will be deprecated in version 2.0", "deprecation_warning"),
        ("Unable to process request due to unknown error", "unclassified")
    ]
    
    other_correct = 0
    for test_msg, expected in other_tests:
        pred = model.predict([test_msg])[0]
        proba = max(model.predict_proba([test_msg])[0])
        
        is_correct = pred == expected
        if is_correct:
            other_correct += 1
        
        status = "✅" if is_correct else "❌"
        print(f"  {status} \"{test_msg}\"")
        print(f"      -> {pred} (expected: {expected}, confidence: {proba:.3f})")
    
    other_accuracy = other_correct / len(other_tests)
    print(f"\n  Non-Security Accuracy: {other_accuracy:.1%} ({other_correct}/{len(other_tests)})")
    
    # Overall assessment
    total_tests = len(security_tests) + len(other_tests)
    total_correct = security_correct + other_correct
    overall_accuracy = total_correct / total_tests
    
    print(f"\n🎯 Overall Test Results:")
    print(f"   Total tests: {total_tests}")
    print(f"   Correct predictions: {total_correct}")
    print(f"   Overall accuracy: {overall_accuracy:.1%}")
    
    if security_accuracy >= 0.8 and other_accuracy >= 0.8:
        print(f"\n🎉 Model Performance: EXCELLENT!")
        print(f"   ✅ Security alert detection working well")
        print(f"   ✅ Other classifications maintained")
        print(f"   ✅ Ready for production use")
    elif security_accuracy >= 0.6:
        print(f"\n👍 Model Performance: GOOD")
        print(f"   ✅ Security alert detection functional")
        print(f"   ⚠️  Some fine-tuning may be beneficial")
    else:
        print(f"\n⚠️  Model Performance: NEEDS IMPROVEMENT")
        print(f"   ❌ Security alert detection needs work")
    
    # Check model info
    print(f"\n📊 Model Information:")
    if hasattr(model, 'steps'):
        for step_name, step_obj in model.steps:
            print(f"   {step_name}: {type(step_obj).__name__}")
            if hasattr(step_obj, 'get_params'):
                params = step_obj.get_params()
                if step_name == 'tfidf':
                    print(f"      max_features: {params.get('max_features', 'N/A')}")
                    print(f"      ngram_range: {params.get('ngram_range', 'N/A')}")
                elif hasattr(step_obj, 'C'):
                    print(f"      C: {params.get('C', 'N/A')}")
                elif hasattr(step_obj, 'n_estimators'):
                    print(f"      n_estimators: {params.get('n_estimators', 'N/A')}")

if __name__ == "__main__":
    test_security_model()