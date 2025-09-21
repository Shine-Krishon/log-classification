import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
from datetime import datetime

def retrain_model_with_hr_data():
    """Retrain the enhanced model with proper HR training data."""
    
    print("🤖 RETRAINING MODEL WITH HR DATA")
    print("=" * 50)
    
    # Load enhanced training data
    try:
        df = pd.read_csv('data/training/dataset/enhanced_synthetic_logs_with_hr.csv')
        print(f"Loaded {len(df)} training examples")
    except Exception as e:
        print(f"Error loading training data: {e}")
        return False
    
    # Show label distribution
    print("Label distribution:")
    label_counts = df['target_label'].value_counts()
    for label, count in label_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {label}: {count} ({percentage:.1f}%)")
    
    # Prepare training data
    X = df['log_message']
    y = df['target_label']
    
    print(f"\nPreparing training data...")
    print(f"  Features: {len(X)} log messages")
    print(f"  Labels: {len(y)} classifications")
    print(f"  Unique labels: {len(y.unique())}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"  Training set: {len(X_train)} examples")
    print(f"  Test set: {len(X_test)} examples")
    
    # Create TF-IDF vectorizer
    print(f"\nCreating TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        stop_words='english',
        lowercase=True
    )
    
    # Fit and transform training data
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    print(f"  TF-IDF features: {X_train_tfidf.shape[1]}")
    
    # Train improved model
    print(f"\nTraining Logistic Regression model...")
    model = LogisticRegression(
        max_iter=1000,
        random_state=42,
        class_weight='balanced'  # Handle any class imbalance
    )
    
    model.fit(X_train_tfidf, y_train)
    
    # Evaluate model
    print(f"\nEvaluating model performance...")
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    # Detailed classification report
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    
    # Test specifically on HR examples
    print("\n🎯 TESTING ON HR EXAMPLES:")
    print("-" * 40)
    
    hr_test_cases = [
        ("Employee onboarding workflow triggered", "user_action"),
        ("Payroll calculation completed for 250 employees", "user_action"),
        ("Performance review cycle initiated", "user_action"),
        ("Leave request approved for EMP001", "user_action"),
        ("Benefits enrollment deadline reminder sent", "user_action"),
        ("Training module completion recorded", "user_action"),
        ("Compliance audit report generated", "security_alert"),
        ("Time tracking synchronization completed", "system_notification"),
        ("Employee directory updated", "system_notification"),
        ("Access control review scheduled", "security_alert"),
    ]
    
    hr_correct = 0
    for message, expected in hr_test_cases:
        message_tfidf = vectorizer.transform([message])
        prediction = model.predict(message_tfidf)[0]
        probabilities = model.predict_proba(message_tfidf)[0]
        confidence = max(probabilities)
        
        status = "✅" if prediction == expected else "❌"
        if prediction == expected:
            hr_correct += 1
            
        print(f"{status} '{message}'")
        print(f"   Predicted: {prediction} (confidence: {confidence:.3f})")
        print(f"   Expected: {expected}")
        print()
    
    hr_accuracy = (hr_correct / len(hr_test_cases)) * 100
    print(f"HR Test Accuracy: {hr_correct}/{len(hr_test_cases)} ({hr_accuracy:.1f}%)")
    
    # Save the improved model
    if hr_accuracy >= 80:  # Only save if HR accuracy is good
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save model
        model_path = f'models/log_classifier_with_hr_fix_{timestamp}.joblib'
        joblib.dump(model, model_path)
        print(f"\n✅ Model saved to: {model_path}")
        
        # Save vectorizer  
        vectorizer_path = f'models/tfidf_vectorizer_with_hr_fix_{timestamp}.joblib'
        joblib.dump(vectorizer, vectorizer_path)
        print(f"✅ Vectorizer saved to: {vectorizer_path}")
        
        # Create a simple test script
        test_script = f'''
# Test the HR-fixed model
import joblib

model = joblib.load('{model_path}')
vectorizer = joblib.load('{vectorizer_path}')

def test_message(message):
    tfidf = vectorizer.transform([message])
    prediction = model.predict(tfidf)[0]
    probabilities = model.predict_proba(tfidf)[0]
    confidence = max(probabilities)
    return {{"prediction": prediction, "confidence": confidence}}

# Test HR messages
hr_messages = [
    "Employee onboarding workflow triggered",
    "Payroll calculation completed for 250 employees",
    "Compliance audit report generated"
]

for msg in hr_messages:
    result = test_message(msg)
    print(f"'{{msg}}' → {{result['prediction']}} ({{result['confidence']:.3f}})")
'''
        
        with open(f'test_hr_model_{timestamp}.py', 'w') as f:
            f.write(test_script)
        
        return model_path, vectorizer_path
    else:
        print(f"\n❌ Model HR accuracy too low ({hr_accuracy:.1f}%), not saving")
        return None, None

if __name__ == "__main__":
    model_path, vectorizer_path = retrain_model_with_hr_data()
    
    if model_path:
        print(f"\n🎉 SUCCESS! HR-enhanced model ready for deployment")
        print(f"   Model: {model_path}")
        print(f"   Vectorizer: {vectorizer_path}")
        print(f"\nNext step: Update the enhanced_production_system.py to use the new model")
    else:
        print(f"\n⚠️  Model training needs improvement")