#!/usr/bin/env python3
"""
Simple F1 Score Calculator
==========================

A straightforward script to calculate F1 scores for your log classification model
using scikit-learn's built-in functions.
"""

import joblib
import pandas as pd
from sklearn.metrics import (
    f1_score, 
    classification_report, 
    precision_score,
    recall_score,
    accuracy_score
)

def calculate_f1_scores():
    """
    Calculate F1 scores for the log classification model
    
    Returns:
        dict: Dictionary containing all F1 score metrics
    """
    
    # Load your trained model
    try:
        model = joblib.load('models/enhanced_log_classifier.joblib')
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None
    
    # Test data (replace with your actual test data)
    test_messages = [
        "User 12345 logged in",
        "Failed login attempt from IP 192.168.1.100", 
        "Database backup completed successfully",
        "Payment processing failed",
        "WARNING: Legacy API will be deprecated",
        "User accessed dashboard page",
        "Suspicious activity: brute force attack",
        "System maintenance scheduled",
        "API request failed with 500 error",
        "DEPRECATED: Function xyz() will be removed"
    ]
    
    # True labels (replace with your actual labels)
    true_labels = [
        "user_action",
        "security_alert", 
        "system_notification",
        "workflow_error",
        "deprecation_warning",
        "user_action",
        "security_alert",
        "system_notification", 
        "workflow_error",
        "deprecation_warning"
    ]
    
    # Make predictions
    try:
        predictions = model.predict(test_messages)
        print(f"✅ Predictions completed for {len(test_messages)} samples")
    except Exception as e:
        print(f"❌ Error making predictions: {e}")
        return None
    
    # Calculate F1 scores
    f1_macro = f1_score(true_labels, predictions, average='macro')
    f1_micro = f1_score(true_labels, predictions, average='micro') 
    f1_weighted = f1_score(true_labels, predictions, average='weighted')
    
    # Per-class F1 scores
    f1_per_class = f1_score(true_labels, predictions, average=None)
    unique_labels = sorted(list(set(true_labels + list(predictions))))
    
    # Other metrics
    accuracy = accuracy_score(true_labels, predictions)
    precision_macro = precision_score(true_labels, predictions, average='macro')
    recall_macro = recall_score(true_labels, predictions, average='macro')
    
    # Print results
    print("\n" + "="*60)
    print("🎯 F1 SCORE RESULTS")
    print("="*60)
    
    print(f"\n📊 Overall Metrics:")
    print(f"   Accuracy:         {accuracy:.4f}")
    print(f"   Precision (macro): {precision_macro:.4f}")
    print(f"   Recall (macro):    {recall_macro:.4f}")
    
    print(f"\n🎯 F1 Scores:")
    print(f"   Macro F1:      {f1_macro:.4f}")
    print(f"   Micro F1:      {f1_micro:.4f}")
    print(f"   Weighted F1:   {f1_weighted:.4f}")
    
    print(f"\n📋 Per-Class F1 Scores:")
    for i, label in enumerate(unique_labels):
        if i < len(f1_per_class):
            print(f"   {label:<20}: {f1_per_class[i]:.4f}")
    
    print(f"\n📄 Detailed Classification Report:")
    print(classification_report(true_labels, predictions))
    
    # Create results dictionary
    results = {
        'accuracy': accuracy,
        'f1_macro': f1_macro,
        'f1_micro': f1_micro,
        'f1_weighted': f1_weighted,
        'precision_macro': precision_macro,
        'recall_macro': recall_macro,
        'per_class_f1': dict(zip(unique_labels[:len(f1_per_class)], f1_per_class)),
        'predictions': list(predictions),
        'true_labels': true_labels
    }
    
    return results

def explain_f1_scores():
    """
    Explain what F1 scores mean and how to interpret them
    """
    print("\n" + "="*60)
    print("📚 F1 SCORE EXPLANATION")
    print("="*60)
    
    print("""
🎯 What is F1 Score?
   F1 Score = 2 × (Precision × Recall) / (Precision + Recall)
   
   • It's the harmonic mean of precision and recall
   • Ranges from 0 to 1 (higher is better)
   • Balances precision and recall into a single metric
   
📊 Types of F1 Scores:

   1. Macro F1: Average of F1 scores for each class
      - Treats all classes equally
      - Good for balanced datasets
      
   2. Micro F1: Calculated globally across all classes  
      - Considers class frequencies
      - Same as accuracy for multi-class problems
      
   3. Weighted F1: Weighted average by class support
      - Accounts for class imbalance
      - Most commonly reported
      
   4. Per-Class F1: Individual F1 for each category
      - Shows which classes perform best/worst
      - Helps identify problem areas

🎖️ Interpretation Guidelines:
   • 0.90 - 1.00: Excellent
   • 0.80 - 0.89: Very Good  
   • 0.70 - 0.79: Good
   • 0.60 - 0.69: Fair
   • Below 0.60: Needs Improvement
   
💡 For your log classification:
   • High F1 for security_alert = Fewer missed threats
   • High F1 for user_action = Fewer false alarms
   • Weighted F1 gives overall system performance
    """)

if __name__ == "__main__":
    print("🚀 F1 Score Calculator for Log Classification Model")
    
    # Calculate F1 scores
    results = calculate_f1_scores()
    
    # Explain F1 scores
    explain_f1_scores()
    
    if results:
        print(f"\n✅ F1 Score calculation completed!")
        print(f"   Your model's Weighted F1 Score: {results['f1_weighted']:.4f}")
        
        if results['f1_weighted'] >= 0.80:
            print("   🎉 Excellent performance!")
        elif results['f1_weighted'] >= 0.70:
            print("   👍 Good performance!")
        else:
            print("   📈 Room for improvement!")
    else:
        print("❌ F1 Score calculation failed")