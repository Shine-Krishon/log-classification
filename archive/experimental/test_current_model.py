import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os

def test_current_model():
    """Test the current trained model on medium_test.csv."""
    
    print("🧪 TESTING CURRENT MODEL PERFORMANCE")
    print("=" * 50)
    
    # Load the current model
    try:
        model = joblib.load('models/log_classifier.joblib')
        print("✅ Loaded current model")
    except Exception as e:
        print(f"❌ Could not load model: {e}")
        return
    
    # Load test data
    try:
        test_df = pd.read_csv('medium_test.csv')
        print(f"✅ Loaded test data: {len(test_df)} records")
    except Exception as e:
        print(f"❌ Could not load test data: {e}")
        return
    
    # Check if it's the expected test data with ModernHR
    modernhr_examples = test_df[test_df['log_message'].str.contains('ModernHR', case=False, na=False)]
    print(f"📊 ModernHR examples in test data: {len(modernhr_examples)}")
    
    if len(modernhr_examples) > 0:
        print("\nModernHR examples:")
        for idx, row in modernhr_examples.head(5).iterrows():
            print(f"  {row['log_message']}")
    
    # Get predictions
    try:
        predictions = model.predict(test_df['log_message'])
        print(f"✅ Generated {len(predictions)} predictions")
        
        # Show prediction distribution
        unique_predictions, counts = np.unique(predictions, return_counts=True)
        print("\nPrediction distribution:")
        for label, count in zip(unique_predictions, counts):
            pct = (count / len(predictions)) * 100
            print(f"  {label}: {count} ({pct:.1f}%)")
        
        # Focus on ModernHR predictions
        if len(modernhr_examples) > 0:
            modernhr_indices = modernhr_examples.index
            modernhr_predictions = [predictions[i] for i in modernhr_indices]
            
            print(f"\n🎯 ModernHR Classification Results:")
            modernhr_pred_counts = pd.Series(modernhr_predictions).value_counts()
            for label, count in modernhr_pred_counts.items():
                pct = (count / len(modernhr_predictions)) * 100
                print(f"  {label}: {count} ({pct:.1f}%)")
            
            print("\nDetailed ModernHR predictions:")
            for idx, (i, row) in enumerate(modernhr_examples.iterrows()):
                pred = predictions[i]
                print(f"  {idx+1}. '{row['log_message']}' → {pred}")
    
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        return
    
    # If we have true labels, calculate accuracy
    if 'true_label' in test_df.columns or 'target_label' in test_df.columns:
        true_col = 'true_label' if 'true_label' in test_df.columns else 'target_label'
        true_labels = test_df[true_col]
        
        accuracy = (predictions == true_labels).mean()
        print(f"\n📈 Overall Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")
        
        # ModernHR specific accuracy
        if len(modernhr_examples) > 0:
            modernhr_true = [true_labels.iloc[i] for i in modernhr_indices]
            modernhr_accuracy = sum(p == t for p, t in zip(modernhr_predictions, modernhr_true)) / len(modernhr_predictions)
            print(f"📈 ModernHR Accuracy: {modernhr_accuracy:.3f} ({modernhr_accuracy*100:.1f}%)")
    
    return predictions

def check_problematic_cases():
    """Check specific problematic cases we identified earlier."""
    
    print("\n🔍 TESTING PROBLEMATIC CASES")
    print("=" * 50)
    
    # Define the problematic cases we found earlier
    problematic_cases = [
        "Employee onboarding workflow triggered",
        "Payroll calculation completed for 250 employees", 
        "Performance review cycle initiated",
        "Leave request approved for EMP001",
        "Benefits enrollment reminder sent",
        "Training module completion recorded",
        "Time tracking synchronization completed",
        "Employee directory updated",
        "Compliance audit report generated",
        "Access control review scheduled",
        "Payroll calculation failed",
        "Employee onboarding workflow error"
    ]
    
    try:
        model = joblib.load('models/log_classifier.joblib')
        
        print("Testing problematic cases:")
        for i, case in enumerate(problematic_cases, 1):
            pred = model.predict([case])[0]
            print(f"  {i:2d}. '{case}' → {pred}")
            
        # Count predictions
        predictions = [model.predict([case])[0] for case in problematic_cases]
        pred_counts = pd.Series(predictions).value_counts()
        
        print(f"\nProblematic cases prediction summary:")
        for label, count in pred_counts.items():
            pct = (count / len(predictions)) * 100
            print(f"  {label}: {count} ({pct:.1f}%)")
            
    except Exception as e:
        print(f"❌ Could not test problematic cases: {e}")

if __name__ == "__main__":
    test_current_model()
    check_problematic_cases()