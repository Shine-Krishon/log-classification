#!/usr/bin/env python3
"""
Quick Security-Enhanced Model Training

This script quickly retrains the model to support security alerts
using optimized parameters for fast execution.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import joblib
import time
import os

def quick_retrain_with_security():
    """Quick retraining with security alert support"""
    print("🚀 Quick Security-Enhanced Model Training")
    print("=" * 50)
    
    # Load dataset
    print("Loading dataset...")
    df = pd.read_csv('logs_chunk1.csv')
    print(f"Dataset: {len(df):,} samples")
    
    # Check classes
    classes = sorted(df['target_label'].unique())
    print(f"Classes: {classes}")
    
    if 'security_alert' not in classes:
        print("❌ No security_alert category found!")
        return None
    
    print("✅ Security alerts detected!")
    print("\nClass distribution:")
    class_counts = df['target_label'].value_counts()
    for label, count in class_counts.items():
        print(f"  {label}: {count}")
    
    # Prepare data
    print("\nPreparing data splits...")
    X = df['log_message']
    y = df['target_label']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Train: {len(X_train):,} samples")
    print(f"Test: {len(X_test):,} samples")
    
    # Quick model 1: Enhanced Logistic Regression
    print("\n=== Training Enhanced Logistic Regression ===")
    
    start_time = time.time()
    
    lr_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            stop_words='english',
            min_df=2,
            max_df=0.95
        )),
        ('lr', LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced'
        ))
    ])
    
    lr_pipeline.fit(X_train, y_train)
    lr_time = time.time() - start_time
    
    lr_pred = lr_pipeline.predict(X_test)
    lr_acc = accuracy_score(y_test, lr_pred)
    
    print(f"Training time: {lr_time:.1f}s")
    print(f"Test accuracy: {lr_acc:.4f}")
    
    # Quick model 2: Optimized Random Forest
    print("\n=== Training Optimized Random Forest ===")
    
    start_time = time.time()
    
    rf_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words='english',
            min_df=2,
            max_df=0.95
        )),
        ('rf', RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        ))
    ])
    
    rf_pipeline.fit(X_train, y_train)
    rf_time = time.time() - start_time
    
    rf_pred = rf_pipeline.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_pred)
    
    print(f"Training time: {rf_time:.1f}s")
    print(f"Test accuracy: {rf_acc:.4f}")
    
    # Choose best model
    if lr_acc >= rf_acc:
        best_model = lr_pipeline
        best_name = "Enhanced_Logistic_Regression"
        best_acc = lr_acc
        best_pred = lr_pred
    else:
        best_model = rf_pipeline
        best_name = "Optimized_Random_Forest"
        best_acc = rf_acc
        best_pred = rf_pred
    
    print(f"\n🏆 Best Model: {best_name}")
    print(f"   Accuracy: {best_acc:.4f}")
    
    # Security-specific evaluation
    print(f"\n🔒 Security Alert Performance:")
    security_mask = y_test == 'security_alert'
    if security_mask.sum() > 0:
        security_true = y_test[security_mask]
        security_pred = best_pred[security_mask]
        security_acc = accuracy_score(security_true, security_pred)
        
        print(f"   Security samples in test: {security_mask.sum()}")
        print(f"   Security accuracy: {security_acc:.4f}")
        
        # Check misclassifications
        correct_security = (security_pred == 'security_alert').sum()
        print(f"   Correctly identified: {correct_security}/{security_mask.sum()}")
        
        if correct_security < security_mask.sum():
            wrong_pred = security_pred[security_pred != 'security_alert']
            print(f"   Misclassified as:")
            for label in np.unique(wrong_pred):
                count = (wrong_pred == label).sum()
                print(f"     {label}: {count}")
        else:
            print("   ✅ All security alerts correctly identified!")
    
    # Detailed classification report
    print(f"\n📊 Classification Report:")
    print(classification_report(y_test, best_pred))
    
    # Save the model
    model_filename = 'log_classifier_with_security_alerts.joblib'
    joblib.dump(best_model, model_filename)
    print(f"\n💾 Model saved: {model_filename}")
    
    # Create backup of existing model if it exists
    existing_model = 'log_classifier_20k_random_forest.joblib'
    if os.path.exists(existing_model):
        backup_name = 'log_classifier_20k_random_forest_backup.joblib'
        os.rename(existing_model, backup_name)
        print(f"   Old model backed up as: {backup_name}")
    
    # Update the main model file too
    joblib.dump(best_model, 'log_classifier_20k_random_forest.joblib')
    print(f"   Main model updated: log_classifier_20k_random_forest.joblib")
    
    # Test some security examples
    print(f"\n🔍 Security Detection Demo:")
    
    security_examples = [
        "Failed login attempt for user admin from IP 192.168.1.100",
        "SQL injection attempt detected in user input",
        "Unauthorized access attempt detected",
        "DDoS attack detected from multiple IPs",
        "Malicious file upload blocked"
    ]
    
    normal_examples = [
        "User logged in successfully",
        "Application started on port 8080",
        "Database backup completed",
        "Payment processing failed: insufficient funds",
        "Configuration file reloaded"
    ]
    
    print("\nSecurity Examples:")
    for example in security_examples:
        pred = best_model.predict([example])[0]
        prob = max(best_model.predict_proba([example])[0])
        status = "✅" if pred == 'security_alert' else "❌"
        print(f"{status} {example}")
        print(f"   -> {pred} ({prob:.3f})")
    
    print("\nNormal Examples:")
    for example in normal_examples:
        pred = best_model.predict([example])[0]
        prob = max(best_model.predict_proba([example])[0])
        status = "✅" if pred != 'security_alert' else "⚠️"
        print(f"{status} {example}")
        print(f"   -> {pred} ({prob:.3f})")
    
    print(f"\n🎉 Model upgrade completed!")
    print(f"   ✅ Security alerts now supported")
    print(f"   ✅ {len(classes)} total categories")
    print(f"   ✅ {best_acc:.1%} overall accuracy")
    
    return best_model

if __name__ == "__main__":
    model = quick_retrain_with_security()
    if model:
        print("\n✅ Retraining successful! Your model now supports security alerts.")
    else:
        print("\n❌ Retraining failed.")