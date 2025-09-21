#!/usr/bin/env python3
"""
F1 Score Calculator with Correct Label Mapping
==============================================

Calculate F1 scores for your log classification model using the correct label format.
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

def get_f1_scores_for_model():
    """
    Calculate F1 scores using the correct label mapping that matches your model
    """
    
    # Load model
    try:
        model = joblib.load('models/enhanced_log_classifier.joblib')
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None
    
    # Test data with CORRECT labels (singular, matching your model training)
    test_data = [
        # User Actions
        ("User 12345 logged in", "user_action"),
        ("User john.doe logged out", "user_action"), 
        ("User accessed dashboard page", "user_action"),
        ("User uploaded file report.pdf", "user_action"),
        ("User updated profile information", "user_action"),
        ("User searched for 'sales data'", "user_action"),
        ("User created new record ID: 789", "user_action"),
        ("User deleted old backup file", "user_action"),
        ("User generated monthly report", "user_action"),
        ("User changed password successfully", "user_action"),
        
        # Security Alerts
        ("Failed login attempt from IP 192.168.1.100", "security_alert"),
        ("Multiple failed login attempts detected", "security_alert"),
        ("Suspicious activity: brute force attack", "security_alert"), 
        ("Unauthorized access attempt blocked", "security_alert"),
        ("SQL injection attempt detected", "security_alert"),
        ("Cross-site scripting attack prevented", "security_alert"),
        ("Malware detected in uploaded file", "security_alert"),
        ("Privilege escalation attempt blocked", "security_alert"),
        ("Data exfiltration attempt detected", "security_alert"),
        ("Session hijacking attempt prevented", "security_alert"),
        
        # System Notifications  
        ("Database backup completed successfully", "system_notification"),
        ("System maintenance scheduled for tonight", "system_notification"),
        ("Server restart completed", "system_notification"),
        ("Cache cleared successfully", "system_notification"),
        ("Configuration updated", "system_notification"),
        ("Service health check passed", "system_notification"),
        ("Disk cleanup completed", "system_notification"),
        ("Log rotation performed", "system_notification"),
        ("Memory usage normal", "system_notification"),
        ("CPU utilization stable", "system_notification"),
        
        # Workflow Errors
        ("Payment processing failed", "workflow_error"),
        ("Database connection timeout", "workflow_error"),
        ("API request failed with 500 error", "workflow_error"),
        ("File upload failed - size too large", "workflow_error"),
        ("Email delivery failed", "workflow_error"),
        ("Backup process encountered error", "workflow_error"),
        ("Import process failed - invalid format", "workflow_error"),
        ("Export timeout exceeded", "workflow_error"),
        ("Service unavailable", "workflow_error"),
        ("Queue processing error", "workflow_error"),
        
        # Deprecation Warnings
        ("WARNING: Legacy API will be deprecated in v2.0", "deprecation_warning"),
        ("DEPRECATED: Function xyz() will be removed", "deprecation_warning"),
        ("NOTICE: Old encryption method will be disabled", "deprecation_warning"),
        ("DEPRECATED: Legacy file format no longer supported", "deprecation_warning"),
        ("WARNING: This feature will be removed in next version", "deprecation_warning"),
        ("NOTICE: Update required for continued support", "deprecation_warning"),
        ("DEPRECATED: Old authentication method", "deprecation_warning"),
        ("WARNING: SSL version deprecated", "deprecation_warning"),
        ("NOTICE: Database schema change required", "deprecation_warning"),
        ("DEPRECATED: Legacy report format", "deprecation_warning")
    ]
    
    # Separate messages and labels
    messages = [item[0] for item in test_data]
    true_labels = [item[1] for item in test_data]
    
    print(f"📋 Testing with {len(messages)} samples across {len(set(true_labels))} categories")
    
    # Make predictions
    try:
        predictions = model.predict(messages)
        print("✅ Predictions completed")
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return None
    
    # Calculate metrics
    accuracy = accuracy_score(true_labels, predictions)
    
    # F1 Scores
    f1_macro = f1_score(true_labels, predictions, average='macro', zero_division=0)
    f1_micro = f1_score(true_labels, predictions, average='micro', zero_division=0) 
    f1_weighted = f1_score(true_labels, predictions, average='weighted', zero_division=0)
    
    # Per-class F1 scores
    unique_labels = sorted(list(set(true_labels + list(predictions))))
    f1_per_class = f1_score(true_labels, predictions, average=None, labels=unique_labels, zero_division=0)
    
    # Category-specific accuracy
    category_metrics = {}
    for category in set(true_labels):
        category_indices = [i for i, label in enumerate(true_labels) if label == category]
        category_true = [true_labels[i] for i in category_indices]
        category_pred = [predictions[i] for i in category_indices]
        
        if category_true:
            cat_accuracy = accuracy_score(category_true, category_pred)
            cat_f1 = f1_score([category]*len(category_true), category_pred, 
                             labels=[category], average='micro', zero_division=0)
            category_metrics[category] = {
                'accuracy': cat_accuracy,
                'f1_score': cat_f1,
                'support': len(category_true),
                'correct_predictions': sum(1 for t, p in zip(category_true, category_pred) if t == p)
            }
    
    # Print comprehensive results
    print("\n" + "="*80)
    print("🎯 COMPREHENSIVE F1 SCORE ANALYSIS")
    print("="*80)
    
    print(f"\n📊 OVERALL METRICS:")
    print(f"   • Overall Accuracy:      {accuracy:.4f} ({accuracy*100:.1f}%)")
    print(f"   • Weighted F1 Score:     {f1_weighted:.4f}")
    print(f"   • Macro F1 Score:        {f1_macro:.4f}")
    print(f"   • Micro F1 Score:        {f1_micro:.4f}")
    
    print(f"\n📋 CATEGORY-SPECIFIC RESULTS:")
    for category, metrics in category_metrics.items():
        print(f"   • {category:<20}: "
              f"Accuracy={metrics['accuracy']:.4f} | "
              f"F1={metrics['f1_score']:.4f} | "
              f"Correct={metrics['correct_predictions']}/{metrics['support']}")
    
    print(f"\n📄 DETAILED CLASSIFICATION REPORT:")
    print(classification_report(true_labels, predictions, zero_division=0))
    
    # Performance interpretation
    print(f"\n🎖️ F1 SCORE INTERPRETATION:")
    if f1_weighted >= 0.90:
        print("   ✅ EXCELLENT: Outstanding model performance!")
        status = "Excellent"
    elif f1_weighted >= 0.80:
        print("   ✅ VERY GOOD: Strong model performance!")
        status = "Very Good"
    elif f1_weighted >= 0.70:
        print("   ⚠️  GOOD: Acceptable performance with room for improvement")
        status = "Good"
    else:
        print("   ❌ NEEDS IMPROVEMENT: Significant optimization required")
        status = "Needs Improvement"
    
    # Find best and worst categories
    if category_metrics:
        best_cat = max(category_metrics.items(), key=lambda x: x[1]['f1_score'])
        worst_cat = min(category_metrics.items(), key=lambda x: x[1]['f1_score'])
        
        print(f"\n🏆 CATEGORY HIGHLIGHTS:")
        print(f"   • Best:  {best_cat[0]} (F1: {best_cat[1]['f1_score']:.4f})")
        print(f"   • Worst: {worst_cat[0]} (F1: {worst_cat[1]['f1_score']:.4f})")
    
    # Create results summary
    results = {
        'overall_accuracy': accuracy,
        'f1_weighted': f1_weighted,
        'f1_macro': f1_macro,
        'f1_micro': f1_micro,
        'category_metrics': category_metrics,
        'performance_status': status,
        'total_samples': len(messages),
        'categories_tested': len(set(true_labels))
    }
    
    return results

def show_f1_usage_examples():
    """
    Show practical examples of how to use F1 scores in your code
    """
    print("\n" + "="*60)
    print("💡 HOW TO USE F1 SCORES IN YOUR CODE")
    print("="*60)
    
    print("""
🔧 **Quick F1 Score Calculation:**

```python
from sklearn.metrics import f1_score, classification_report
import joblib

# Load your model
model = joblib.load('models/enhanced_log_classifier.joblib')

# Your test data
messages = ["User logged in", "Failed login attempt"]
true_labels = ["user_action", "security_alert"]

# Make predictions
predictions = model.predict(messages)

# Calculate F1 scores
f1_weighted = f1_score(true_labels, predictions, average='weighted')
f1_macro = f1_score(true_labels, predictions, average='macro')

print(f"Weighted F1: {f1_weighted:.4f}")
print(f"Macro F1: {f1_macro:.4f}")

# Detailed report
print(classification_report(true_labels, predictions))
```

🎯 **For Real-Time Monitoring:**

```python
def evaluate_model_performance(model, test_messages, test_labels):
    predictions = model.predict(test_messages)
    f1_score_weighted = f1_score(test_labels, predictions, average='weighted')
    
    if f1_score_weighted < 0.80:
        print("⚠️ Model performance degraded - consider retraining")
    else:
        print(f"✅ Model performing well (F1: {f1_score_weighted:.3f})")
    
    return f1_score_weighted
```

📊 **For Category-Specific Analysis:**

```python
def analyze_security_performance(true_labels, predictions):
    security_f1 = f1_score(
        true_labels, predictions,
        labels=['security_alert'],
        average='micro'
    )
    
    if security_f1 < 0.95:
        print("🚨 Security detection needs improvement!")
    
    return security_f1
```
    """)

def main():
    """Main function"""
    print("🚀 F1 Score Calculator for Log Classification Model")
    
    # Calculate F1 scores
    results = get_f1_scores_for_model()
    
    # Show usage examples
    show_f1_usage_examples()
    
    if results:
        print(f"\n✅ F1 Score Analysis Complete!")
        print(f"🎯 Key Result: Weighted F1 = {results['f1_weighted']:.4f} ({results['performance_status']})")

if __name__ == "__main__":
    main()