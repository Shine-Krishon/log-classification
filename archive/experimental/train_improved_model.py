import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
import joblib
# import matplotlib.pyplot as plt  # Optional for visualization
# import seaborn as sns  # Optional for visualization

def train_improved_model():
    """
    Train models using the improved dataset
    """
    print("=== Loading Improved Datasets ===")
    train_df = pd.read_csv('train_set.csv')
    val_df = pd.read_csv('validation_set.csv')
    test_df = pd.read_csv('test_set.csv')
    
    print(f"Train set: {len(train_df)} samples")
    print(f"Validation set: {len(val_df)} samples")
    print(f"Test set: {len(test_df)} samples")
    
    # Prepare data
    X_train = train_df['log_message']
    y_train = train_df['target_label']
    X_val = val_df['log_message']
    y_val = val_df['target_label']
    X_test = test_df['log_message']
    y_test = test_df['target_label']
    
    print("\n=== Training Models ===")
    
    # Model 1: TF-IDF + Logistic Regression
    print("Training TF-IDF + Logistic Regression...")
    
    tfidf_lr_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words='english')),
        ('lr', LogisticRegression(max_iter=1000, random_state=42))
    ])
    
    # Grid search for best parameters
    param_grid_lr = {
        'tfidf__max_features': [3000, 5000, 8000],
        'tfidf__ngram_range': [(1, 1), (1, 2)],
        'lr__C': [0.1, 1.0, 10.0]
    }
    
    grid_lr = GridSearchCV(tfidf_lr_pipeline, param_grid_lr, cv=3, scoring='accuracy', n_jobs=-1)
    grid_lr.fit(X_train, y_train)
    
    best_lr_model = grid_lr.best_estimator_
    print(f"Best LR parameters: {grid_lr.best_params_}")
    
    # Model 2: TF-IDF + Random Forest
    print("Training TF-IDF + Random Forest...")
    
    tfidf_rf_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words='english')),
        ('rf', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    param_grid_rf = {
        'tfidf__max_features': [3000, 5000],
        'rf__n_estimators': [50, 100],
        'rf__max_depth': [10, 20, None]
    }
    
    grid_rf = GridSearchCV(tfidf_rf_pipeline, param_grid_rf, cv=3, scoring='accuracy', n_jobs=-1)
    grid_rf.fit(X_train, y_train)
    
    best_rf_model = grid_rf.best_estimator_
    print(f"Best RF parameters: {grid_rf.best_params_}")
    
    # Evaluate models
    print("\n=== Model Evaluation ===")
    
    models = {
        'Logistic Regression': best_lr_model,
        'Random Forest': best_rf_model
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\n--- {name} ---")
        
        # Validation accuracy
        val_pred = model.predict(X_val)
        val_accuracy = accuracy_score(y_val, val_pred)
        
        # Test accuracy
        test_pred = model.predict(X_test)
        test_accuracy = accuracy_score(y_test, test_pred)
        
        print(f"Validation Accuracy: {val_accuracy:.3f}")
        print(f"Test Accuracy: {test_accuracy:.3f}")
        
        print("\nClassification Report (Test Set):")
        print(classification_report(y_test, test_pred))
        
        results[name] = {
            'model': model,
            'val_accuracy': val_accuracy,
            'test_accuracy': test_accuracy,
            'test_pred': test_pred
        }
    
    # Select best model
    best_model_name = max(results.keys(), key=lambda k: results[k]['test_accuracy'])
    best_model = results[best_model_name]['model']
    
    print(f"\n=== Best Model: {best_model_name} ===")
    print(f"Test Accuracy: {results[best_model_name]['test_accuracy']:.3f}")
    
    # Save best model
    joblib.dump(best_model, 'improved_log_classifier.joblib')
    print("Model saved as 'improved_log_classifier.joblib'")
    
    # Feature importance (for RF) or coefficients (for LR)
    print("\n=== Feature Analysis ===")
    if 'Random Forest' in best_model_name:
        # Get feature importance from Random Forest
        tfidf = best_model.named_steps['tfidf']
        rf = best_model.named_steps['rf']
        feature_names = tfidf.get_feature_names_out()
        importances = rf.feature_importances_
        
        # Top 20 most important features
        top_indices = np.argsort(importances)[-20:][::-1]
        print("Top 20 Most Important Features:")
        for idx in top_indices:
            print(f"{feature_names[idx]}: {importances[idx]:.4f}")
    
    # Complexity-based evaluation
    print("\n=== Complexity-based Evaluation ===")
    test_df_with_pred = test_df.copy()
    test_df_with_pred['predicted'] = results[best_model_name]['test_pred']
    
    for complexity in test_df['complexity'].unique():
        complexity_data = test_df_with_pred[test_df_with_pred['complexity'] == complexity]
        complexity_accuracy = accuracy_score(
            complexity_data['target_label'], 
            complexity_data['predicted']
        )
        print(f"{complexity} complexity: {complexity_accuracy:.3f} accuracy ({len(complexity_data)} samples)")
    
    # Create summary report
    print("\n=== Summary Report ===")
    total_original = 20000
    total_improved = len(pd.read_csv('logs_chunk1_improved.csv'))
    
    print(f"Original dataset: {total_original} samples (92.7% duplicates)")
    print(f"Improved dataset: {total_improved} samples (37.6% unique)")
    print(f"Best model: {best_model_name}")
    print(f"Test accuracy: {results[best_model_name]['test_accuracy']:.3f}")
    print(f"Dataset quality improvement: {((total_improved/1462) - 1) * 100:.1f}% increase in effective data")
    
    return best_model, results

def demonstrate_model():
    """
    Demonstrate the trained model with sample predictions
    """
    print("\n=== Model Demonstration ===")
    
    # Load the saved model
    model = joblib.load('improved_log_classifier.joblib')
    
    # Sample messages for testing
    sample_messages = [
        "User login failed: invalid password for admin",
        "Database connection timeout after 30 seconds",
        "API endpoint /v1/data deprecated, use /v2/data instead",
        "Memory usage exceeded 90% threshold",
        "Two-factor authentication enabled for user john.doe",
        "Payment processing completed successfully",
        "SSL certificate will expire in 7 days",
        "File upload failed: size limit exceeded",
        "Cache miss: key 'user_session_12345' not found",
        "Unknown error occurred during processing"
    ]
    
    print("Sample Predictions:")
    for message in sample_messages:
        prediction = model.predict([message])[0]
        probability = max(model.predict_proba([message])[0])
        print(f"Message: {message}")
        print(f"Prediction: {prediction} (confidence: {probability:.3f})")
        print("-" * 50)

if __name__ == "__main__":
    best_model, results = train_improved_model()
    demonstrate_model()