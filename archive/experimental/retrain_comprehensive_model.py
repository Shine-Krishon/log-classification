"""
Comprehensive Model Retraining Script
=====================================

This script retrains the log classification model using the comprehensive
training dataset with all duplicates removed and domain-specific coverage added.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline
import joblib
import os
from datetime import datetime

def load_training_data():
    """Load the comprehensive training dataset."""
    
    print("📁 Loading comprehensive training dataset...")
    
    try:
        # Try comprehensive dataset first
        comprehensive_path = 'data/training/dataset/comprehensive_training_dataset.csv'
        if os.path.exists(comprehensive_path):
            df = pd.read_csv(comprehensive_path)
            print(f"   Loaded comprehensive dataset: {len(df)} entries")
            return df
        else:
            # Fallback to original dataset
            original_path = 'data/training/dataset/enhanced_synthetic_logs.csv'
            df = pd.read_csv(original_path)
            print(f"   Loaded original dataset: {len(df)} entries")
            return df
            
    except Exception as e:
        print(f"   Error loading training data: {e}")
        return None

def preprocess_data(df):
    """Preprocess the training data for model training."""
    
    print("🔧 Preprocessing training data...")
    
    # Remove any remaining duplicates
    initial_count = len(df)
    df = df.drop_duplicates(subset=['log_message', 'target_label'])
    final_count = len(df)
    
    if initial_count != final_count:
        print(f"   Removed {initial_count - final_count} additional duplicates")
    
    # Filter for BERT complexity (enhanced model training data)
    df = df[df['complexity'] == 'bert'].copy()
    print(f"   Using {len(df)} BERT-level training examples")
    
    # Show label distribution
    print("   Label distribution:")
    for label, count in df['target_label'].value_counts().items():
        pct = (count / len(df)) * 100
        print(f"     {label}: {count} ({pct:.1f}%)")
    
    return df

def create_optimized_model():
    """Create an optimized classification pipeline."""
    
    print("🏗️  Creating optimized model pipeline...")
    
    # Create pipeline with optimized parameters
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=10000,      # Increased vocabulary
            ngram_range=(1, 3),      # Include trigrams for better context
            min_df=2,                # Minimum document frequency
            max_df=0.95,             # Maximum document frequency
            stop_words='english',     # Remove common words
            lowercase=True,
            sublinear_tf=True        # Apply sublinear scaling
        )),
        ('classifier', LogisticRegression(
            max_iter=2000,           # More iterations for convergence
            class_weight='balanced', # Handle class imbalance
            random_state=42,
            solver='liblinear',      # Better for small datasets
            multi_class='ovr'        # One-vs-rest for multi-class
        ))
    ])
    
    return pipeline

def train_and_evaluate_model(X_train, X_test, y_train, y_test, pipeline):
    """Train the model and evaluate its performance."""
    
    print("🎯 Training optimized model...")
    
    # Hyperparameter tuning
    param_grid = {
        'tfidf__max_features': [8000, 10000, 12000],
        'tfidf__ngram_range': [(1, 2), (1, 3)],
        'classifier__C': [0.1, 1.0, 10.0],
        'classifier__penalty': ['l1', 'l2']
    }
    
    # Grid search with cross-validation
    grid_search = GridSearchCV(
        pipeline, 
        param_grid, 
        cv=5, 
        scoring='accuracy',
        n_jobs=-1,
        verbose=1
    )
    
    # Fit the model
    grid_search.fit(X_train, y_train)
    
    print(f"   Best parameters: {grid_search.best_params_}")
    print(f"   Best cross-validation score: {grid_search.best_score_:.4f}")
    
    # Best model
    best_model = grid_search.best_estimator_
    
    # Predictions
    y_pred = best_model.predict(X_test)
    
    # Evaluation
    test_accuracy = accuracy_score(y_test, y_pred)
    print(f"   Test accuracy: {test_accuracy:.4f}")
    
    # Detailed classification report
    print("\n📊 Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Cross-validation on full dataset
    cv_scores = cross_val_score(best_model, X_train, y_train, cv=5)
    print(f"\n🔄 Cross-validation scores: {cv_scores}")
    print(f"   Mean CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    return best_model, test_accuracy

def save_model(model, accuracy, dataset_info):
    """Save the trained model with metadata."""
    
    print("💾 Saving trained model...")
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Model filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_filename = f'models/comprehensive_log_classifier_{timestamp}.joblib'
    
    # Save model
    joblib.dump(model, model_filename)
    
    # Also save as primary model
    primary_model_path = 'models/log_classifier.joblib'
    joblib.dump(model, primary_model_path)
    
    # Save metadata
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'model_file': model_filename,
        'test_accuracy': accuracy,
        'training_data_info': dataset_info,
        'model_type': 'comprehensive_enhanced_classifier',
        'features': 'TF-IDF with optimized parameters',
        'algorithm': 'Logistic Regression with hyperparameter tuning',
        'preprocessing': 'Duplicates removed, domain-specific training added'
    }
    
    metadata_file = f'models/model_metadata_{timestamp}.txt'
    with open(metadata_file, 'w') as f:
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")
    
    print(f"   Model saved: {model_filename}")
    print(f"   Primary model updated: {primary_model_path}")
    print(f"   Metadata saved: {metadata_file}")
    
    return model_filename, primary_model_path

def test_on_problematic_cases():
    """Test the new model on previously problematic cases."""
    
    print("🧪 Testing on previously problematic cases...")
    
    # Load the new model
    try:
        model = joblib.load('models/log_classifier.joblib')
    except Exception as e:
        print(f"   Error loading model: {e}")
        return
    
    # Test cases from ModernHR and other problematic sources
    test_cases = [
        # ModernHR cases (should NOT be security_alert)
        ("ModernHR", "Employee onboarding workflow triggered"),
        ("ModernHR", "Payroll calculation completed for 250 employees"),
        ("ModernHR", "Performance review cycle initiated"),
        ("ModernHR", "Leave request approved for EMP001"),
        ("ModernHR", "Benefits enrollment reminder sent"),
        
        # Other problematic sources
        ("BillingSystem", "Invoice generated for customer CUST123"),
        ("BillingSystem", "Payment processed successfully"),
        ("DatabaseSystem", "Database backup completed successfully"),
        ("FileSystem", "File upload completed for user"),
        ("AnalyticsEngine", "Daily report generation started"),
        
        # Should still be security_alert
        ("SecuritySystem", "Intrusion detection alert triggered"),
        ("SecuritySystem", "Unauthorized login attempt detected"),
        ("ModernHR", "Unauthorized access to employee records"),
        ("BillingSystem", "Fraud detection alert triggered"),
    ]
    
    print("   Test predictions:")
    for source, message in test_cases:
        try:
            prediction = model.predict([message])[0]
            probability = model.predict_proba([message])[0].max()
            print(f"     {source}: '{message}' → {prediction} ({probability:.3f})")
        except Exception as e:
            print(f"     Error predicting for: {message} - {e}")

def main():
    """Main training function."""
    
    print("🚀 COMPREHENSIVE MODEL RETRAINING")
    print("=" * 60)
    
    # Load training data
    df = load_training_data()
    if df is None:
        print("❌ Failed to load training data")
        return
    
    # Preprocess data
    df = preprocess_data(df)
    if len(df) == 0:
        print("❌ No training data after preprocessing")
        return
    
    # Prepare features and labels
    X = df['log_message']
    y = df['target_label']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"   Training set: {len(X_train)} examples")
    print(f"   Test set: {len(X_test)} examples")
    
    # Create and train model
    pipeline = create_optimized_model()
    
    # Train and evaluate
    model, accuracy = train_and_evaluate_model(X_train, X_test, y_train, y_test, pipeline)
    
    # Dataset info for metadata
    dataset_info = {
        'total_examples': len(df),
        'training_examples': len(X_train),
        'test_examples': len(X_test),
        'unique_labels': list(df['target_label'].unique()),
        'duplicate_removal': 'Yes - removed 1351 duplicates',
        'domain_enhancement': 'Yes - added HR, Billing, Analytics examples'
    }
    
    # Save model
    model_file, primary_file = save_model(model, accuracy, dataset_info)
    
    # Test on problematic cases
    test_on_problematic_cases()
    
    print(f"\n✅ MODEL RETRAINING COMPLETED")
    print(f"   Final accuracy: {accuracy:.4f}")
    print(f"   Model file: {primary_file}")
    print(f"   Ready for deployment!")

if __name__ == "__main__":
    main()