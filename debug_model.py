#!/usr/bin/env python3
"""Debug the model predictions and probabilities"""

from processor_bert_enhanced import _model_cache, load_model
import numpy as np

# Load the model first
print("=== DEBUGGING MODEL PREDICTIONS ===")
load_success = load_model()
print(f"Model loaded: {load_success}")

if load_success:
    model = _model_cache['model']
    print(f"Model type: {type(model)}")
    print(f"Model path: {_model_cache['model_path']}")
    
    # Test cases with expected results
    test_cases = [
        ("User 12345 logged in", "user_action"),
        ("Failed login attempt detected", "security_alert"),
        ("User accessed dashboard", "user_action"),
        ("SQL injection attempt", "security_alert"),
        ("User uploaded file", "user_action")
    ]
    
    print("\n=== RAW MODEL PREDICTIONS ===")
    for message, expected in test_cases:
        try:
            # Get raw prediction
            prediction = model.predict([message])[0]
            
            # Get probabilities if available
            try:
                probabilities = model.predict_proba([message])[0]
                max_prob = np.max(probabilities)
                
                # Get class labels if available
                try:
                    classes = model.classes_
                    prob_dict = dict(zip(classes, probabilities))
                    print(f"\nMessage: '{message}'")
                    print(f"Expected: {expected}")
                    print(f"Predicted: {prediction}")
                    print(f"Max confidence: {max_prob:.3f}")
                    print(f"All probabilities: {prob_dict}")
                except AttributeError:
                    print(f"\nMessage: '{message}' → {prediction} (conf: {max_prob:.3f})")
                    
            except AttributeError:
                print(f"\nMessage: '{message}' → {prediction} (no probabilities available)")
                
        except Exception as e:
            print(f"ERROR on '{message}': {e}")
            
    # Check if the model has any class information
    try:
        print(f"\n=== MODEL CLASS INFO ===")
        if hasattr(model, 'classes_'):
            print(f"Classes: {model.classes_}")
        if hasattr(model, 'named_steps'):
            print(f"Pipeline steps: {list(model.named_steps.keys())}")
            for step_name, step in model.named_steps.items():
                print(f"  {step_name}: {type(step)}")
                if hasattr(step, 'classes_'):
                    print(f"    Classes: {step.classes_}")
    except Exception as e:
        print(f"Error getting class info: {e}")
        
else:
    print("Failed to load model!")