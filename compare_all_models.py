#!/usr/bin/env python3
"""Test the enhanced_log_classifier.joblib model directly"""

import joblib
import numpy as np

# Test different models
models_to_test = [
    "models/log_classifier.joblib",
    "models/enhanced_log_classifier.joblib", 
    "models/advanced_log_classifier_20250914_113515.joblib"
]

test_cases = [
    ("User 12345 logged in", "user_action"),
    ("User accessed dashboard", "user_action"),
    ("Failed login attempt detected", "security_alert"),
    ("SQL injection attempt", "security_alert"),
    ("User uploaded file", "user_action")
]

print("=== COMPARING ALL AVAILABLE MODELS ===")

for model_path in models_to_test:
    print(f"\n{'='*60}")
    print(f"TESTING MODEL: {model_path}")
    print(f"{'='*60}")
    
    try:
        model = joblib.load(model_path)
        print(f"Model loaded successfully")
        print(f"Classes: {model.classes_}")
        
        correct_predictions = 0
        total_predictions = len(test_cases)
        
        for message, expected in test_cases:
            try:
                prediction = model.predict([message])[0]
                probabilities = model.predict_proba([message])[0]
                max_prob = np.max(probabilities)
                
                is_correct = prediction == expected
                correct_predictions += is_correct
                
                status = "✅" if is_correct else "❌"
                print(f"{status} '{message}' → {prediction} (expected: {expected}, conf: {max_prob:.3f})")
                
            except Exception as e:
                print(f"❌ ERROR on '{message}': {e}")
        
        accuracy = correct_predictions / total_predictions
        print(f"\nModel Accuracy: {accuracy:.1%} ({correct_predictions}/{total_predictions})")
        
        # File size info
        import os
        size_kb = os.path.getsize(model_path) / 1024
        print(f"File size: {size_kb:.1f} KB")
        
    except Exception as e:
        print(f"❌ Failed to load model: {e}")

print("\n" + "="*60)
print("RECOMMENDATION:")
print("The model with the highest accuracy should be used as primary.")