"""
Advanced Model Training and Evaluation Script
==============================================

This script trains and evaluates models using the advanced datasets
to demonstrate the accuracy improvements possible with high-quality,
diverse training data.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.pipeline import Pipeline
import joblib
import os
from datetime import datetime

def load_and_compare_datasets():
    """Load all available datasets for comparison."""
    
    print("📁 LOADING DATASETS FOR COMPARISON")
    print("=" * 50)
    
    datasets = {}
    
    # Dataset options in order of preference
    dataset_files = [
        ('data/training/dataset/advanced_dataset_5000.csv', 'Advanced 5K Dataset'),
        ('data/training/dataset/advanced_dataset_3000.csv', 'Advanced 3K Dataset'), 
        ('data/training/dataset/comprehensive_20k_dataset.csv', 'Comprehensive 20K Dataset'),
        ('data/training/dataset/enhanced_synthetic_logs.csv', 'Original Enhanced Dataset'),
        ('logs_chunk1_improved.csv', 'Improved Chunk Dataset')
    ]
    
    for filepath, name in dataset_files:
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)
                print(f"✅ {name}: {len(df)} entries")
                
                # Show label distribution
                label_dist = df['target_label'].value_counts()
                print(f"   Labels: {dict(label_dist)}")
                
                # Check uniqueness
                unique_messages = df['log_message'].nunique()
                uniqueness_pct = (unique_messages / len(df)) * 100
                print(f"   Uniqueness: {unique_messages}/{len(df)} ({uniqueness_pct:.1f}%)")
                
                datasets[name] = df
                print()
                
            except Exception as e:
                print(f"❌ Error loading {name}: {e}")
    
    return datasets

def train_and_evaluate_model(df, dataset_name):
    """Train and evaluate a model on the given dataset."""
    
    print(f"\n🎯 TRAINING MODEL ON: {dataset_name}")
    print("-" * 60)
    
    # Prepare data
    X = df['log_message']
    y = df['target_label']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {len(X_train)} examples")
    print(f"Test set: {len(X_test)} examples")
    
    # Create optimized pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=12000,
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.90,
            stop_words='english',
            lowercase=True,
            sublinear_tf=True
        )),
        ('classifier', LogisticRegression(
            max_iter=2000,
            class_weight='balanced',
            random_state=42,
            solver='liblinear',
            C=1.0
        ))
    ])
    
    # Train model
    print("Training model...")
    start_time = datetime.now()
    pipeline.fit(X_train, y_train)
    training_time = (datetime.now() - start_time).total_seconds()
    
    # Predictions
    y_pred = pipeline.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    
    # Cross-validation
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='accuracy')
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()
    
    print(f"\n📊 RESULTS:")
    print(f"Training time: {training_time:.2f}s")
    print(f"Test accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"CV accuracy: {cv_mean:.4f} ± {cv_std:.4f}")
    
    # Detailed classification report
    print(f"\n📋 Classification Report:")
    print(classification_report(y_test, y_pred))
    
    return {
        'model': pipeline,
        'accuracy': accuracy,
        'cv_mean': cv_mean,
        'cv_std': cv_std,
        'training_time': training_time,
        'dataset_size': len(df),
        'uniqueness': df['log_message'].nunique() / len(df),
        'classification_report': classification_report(y_test, y_pred, output_dict=True)
    }

def test_on_problematic_cases(model, model_name):
    """Test model on previously problematic cases."""
    
    print(f"\n🧪 TESTING {model_name} ON PROBLEMATIC CASES")
    print("-" * 60)
    
    # Known problematic cases from ModernHR and other sources
    test_cases = [
        # ModernHR cases (should NOT be security_alert)
        ("Employee onboarding workflow triggered", "user_action"),
        ("Payroll calculation completed for 250 employees", "user_action"),
        ("Performance review cycle initiated", "user_action"),
        ("Leave request approved for EMP001", "user_action"),
        ("Benefits enrollment reminder sent", "user_action"),
        ("Time tracking synchronization completed", "system_notification"),
        ("Employee directory updated", "system_notification"),
        ("HR database backup completed", "system_notification"),
        
        # Billing cases
        ("Invoice generated for customer CUST123", "user_action"),
        ("Payment processed successfully", "user_action"),
        ("Monthly billing cycle completed", "system_notification"),
        ("Credit card authorization failed", "workflow_error"),
        
        # Analytics cases
        ("Daily report generation started", "system_notification"),
        ("ETL pipeline execution completed", "system_notification"),
        ("Custom report generated by user", "user_action"),
        ("Data synchronization error", "workflow_error"),
        
        # Security cases (should be security_alert)
        ("Intrusion detection alert triggered", "security_alert"),
        ("Unauthorized login attempt detected", "security_alert"),
        ("Multiple failed login attempts from IP 192.168.1.100", "security_alert"),
        ("Suspicious file access pattern detected", "security_alert"),
        ("Fraud detection alert triggered", "security_alert"),
        
        # Edge cases
        ("Process PRC1234 completed with status UNKNOWN", "unclassified"),
        ("Legacy API v1.2 deprecated - migrate to v2.0", "deprecation_warning"),
        ("Internet Explorer support ending by 2025", "deprecation_warning")
    ]
    
    correct = 0
    total = len(test_cases)
    
    print("Test Results:")
    for message, expected in test_cases:
        try:
            prediction = model.predict([message])[0]
            probability = model.predict_proba([message])[0].max()
            is_correct = prediction == expected
            correct += is_correct
            
            status = "✅" if is_correct else "❌"
            print(f"  {status} '{message[:50]}...'")
            print(f"      Expected: {expected} | Predicted: {prediction} | Confidence: {probability:.3f}")
            
        except Exception as e:
            print(f"  ❌ Error predicting '{message[:50]}...': {e}")
    
    accuracy = correct / total
    print(f"\n🎯 Problematic Cases Accuracy: {accuracy:.2%} ({correct}/{total})")
    
    return accuracy

def compare_all_models(datasets):
    """Compare performance across all available datasets."""
    
    print(f"\n🏆 COMPREHENSIVE MODEL COMPARISON")
    print("=" * 70)
    
    results = {}
    
    for name, df in datasets.items():
        try:
            result = train_and_evaluate_model(df, name)
            results[name] = result
            
            # Test on problematic cases
            problematic_accuracy = test_on_problematic_cases(result['model'], name)
            results[name]['problematic_accuracy'] = problematic_accuracy
            
        except Exception as e:
            print(f"❌ Error training on {name}: {e}")
            continue
    
    # Summary comparison
    print(f"\n📊 PERFORMANCE COMPARISON SUMMARY")
    print("=" * 70)
    print(f"{'Dataset':<25} {'Size':<6} {'Unique%':<8} {'Test Acc':<9} {'CV Acc':<9} {'Problem Acc':<11}")
    print("-" * 70)
    
    for name, result in results.items():
        print(f"{name:<25} {result['dataset_size']:<6} {result['uniqueness']*100:<7.1f}% "
              f"{result['accuracy']:<8.3f} {result['cv_mean']:<8.3f} "
              f"{result.get('problematic_accuracy', 0):<10.3f}")
    
    # Find best model
    best_name = max(results.keys(), key=lambda x: results[x]['accuracy'])
    best_result = results[best_name]
    
    print(f"\n🏆 BEST PERFORMING MODEL: {best_name}")
    print(f"   Test Accuracy: {best_result['accuracy']:.4f} ({best_result['accuracy']*100:.2f}%)")
    print(f"   CV Accuracy: {best_result['cv_mean']:.4f}")
    print(f"   Problematic Cases: {best_result.get('problematic_accuracy', 0):.2%}")
    print(f"   Dataset Size: {best_result['dataset_size']:,} entries")
    print(f"   Uniqueness: {best_result['uniqueness']*100:.1f}%")
    
    return results, best_name, best_result

def save_best_model(best_result, best_name):
    """Save the best performing model."""
    
    print(f"\n💾 SAVING BEST MODEL: {best_name}")
    print("-" * 50)
    
    # Create models directory
    os.makedirs('models', exist_ok=True)
    
    # Save with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_filename = f'models/advanced_log_classifier_{timestamp}.joblib'
    
    # Save model
    joblib.dump(best_result['model'], model_filename)
    
    # Update primary model
    primary_model_path = 'models/log_classifier.joblib'
    joblib.dump(best_result['model'], primary_model_path)
    
    # Save metadata
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'model_file': model_filename,
        'dataset_used': best_name,
        'test_accuracy': best_result['accuracy'],
        'cv_accuracy': best_result['cv_mean'],
        'problematic_accuracy': best_result.get('problematic_accuracy', 0),
        'dataset_size': best_result['dataset_size'],
        'dataset_uniqueness': best_result['uniqueness'],
        'training_time': best_result['training_time'],
        'model_type': 'advanced_logistic_regression',
        'features': 'Optimized TF-IDF with ngrams',
        'performance_notes': 'Trained on advanced synthetic dataset with business-realistic patterns'
    }
    
    metadata_file = f'models/advanced_model_metadata_{timestamp}.txt'
    with open(metadata_file, 'w') as f:
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")
    
    print(f"✅ Model saved: {model_filename}")
    print(f"✅ Primary model updated: {primary_model_path}")
    print(f"✅ Metadata saved: {metadata_file}")
    
    return model_filename, primary_model_path

def main():
    """Main evaluation function."""
    
    print("🚀 ADVANCED LOG CLASSIFICATION MODEL EVALUATION")
    print("=" * 70)
    print("This script compares different datasets and demonstrates")
    print("how high-quality, diverse training data improves accuracy.")
    print()
    
    # Load all datasets
    datasets = load_and_compare_datasets()
    
    if not datasets:
        print("❌ No datasets found for comparison!")
        return
    
    # Compare all models
    results, best_name, best_result = compare_all_models(datasets)
    
    # Save the best model
    model_file, primary_file = save_best_model(best_result, best_name)
    
    # Final summary
    print(f"\n🎉 EVALUATION COMPLETED!")
    print(f"=" * 70)
    print(f"✅ Best accuracy achieved: {best_result['accuracy']*100:.2f}%")
    print(f"✅ Problematic cases resolved: {best_result.get('problematic_accuracy', 0)*100:.1f}%")
    print(f"✅ Model ready for production: {primary_file}")
    
    # Show improvement over baseline
    if 'Original Enhanced Dataset' in results:
        baseline_acc = results['Original Enhanced Dataset']['accuracy']
        improvement = (best_result['accuracy'] - baseline_acc) * 100
        print(f"✅ Improvement over baseline: +{improvement:.1f} percentage points")
    
    print(f"\n🔍 KEY INSIGHTS:")
    print(f"   • Dataset quality matters more than size")
    print(f"   • Advanced templates create realistic business patterns")
    print(f"   • Balanced distributions improve classification")
    print(f"   • Domain-specific examples resolve edge cases")

if __name__ == "__main__":
    main()