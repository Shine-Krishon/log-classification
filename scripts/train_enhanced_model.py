"""
Enhanced BERT model training script for log classification.
This script uses the new comprehensive dataset with proper business log examples.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sentence_transformers import SentenceTransformer
import joblib
import os
from datetime import datetime

# Configuration
DATA_PATH = "data/training/dataset/enhanced_synthetic_logs.csv"
MODEL_OUTPUT_PATH = "models/enhanced_log_classifier.joblib"
BERT_MODEL_NAME = "all-MiniLM-L6-v2"
TEST_SIZE = 0.2
RANDOM_STATE = 42

def load_and_prepare_data():
    """Load and prepare the training data."""
    print("Loading training data...")
    df = pd.read_csv(DATA_PATH)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Target distribution:\n{df['target_label'].value_counts()}")
    
    # Combine source and log_message for better context
    df['combined_text'] = df['source'] + ': ' + df['log_message']
    
    return df

def generate_embeddings(texts, model_name=BERT_MODEL_NAME):
    """Generate BERT embeddings for the text data."""
    print(f"Loading BERT model: {model_name}")
    model = SentenceTransformer(model_name)
    
    print("Generating embeddings...")
    embeddings = model.encode(texts.tolist(), show_progress_bar=True)
    
    return embeddings

def train_classifier(X_train, y_train, X_test, y_test):
    """Train the logistic regression classifier."""
    print("Training classifier...")
    
    # Use balanced class weights to handle any imbalanced data
    clf = LogisticRegression(
        max_iter=1000,
        class_weight='balanced',
        random_state=RANDOM_STATE
    )
    
    clf.fit(X_train, y_train)
    
    # Evaluate on test set
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    return clf

def save_model(classifier, bert_model_name, output_path):
    """Save the trained model with metadata."""
    print(f"Saving model to: {output_path}")
    
    # Create models directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    model_data = {
        'classifier': classifier,
        'bert_model_name': bert_model_name,
        'trained_at': datetime.now().isoformat(),
        'categories': list(classifier.classes_),
        'feature_count': len(classifier.coef_[0])
    }
    
    joblib.dump(model_data, output_path)
    print("Model saved successfully!")

def main():
    """Main training pipeline."""
    print("=== Enhanced BERT Log Classifier Training ===")
    
    # Load data
    df = load_and_prepare_data()
    
    # Split data
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        df['combined_text'], 
        df['target_label'],
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=df['target_label']
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    
    # Generate embeddings
    X_train_embeddings = generate_embeddings(X_train, BERT_MODEL_NAME)
    X_test_embeddings = generate_embeddings(X_test, BERT_MODEL_NAME)
    
    # Train classifier
    classifier = train_classifier(X_train_embeddings, y_train, X_test_embeddings, y_test)
    
    # Save model
    save_model(classifier, BERT_MODEL_NAME, MODEL_OUTPUT_PATH)
    
    print("\n=== Training Complete ===")
    print(f"Model saved as: {MODEL_OUTPUT_PATH}")
    print(f"Categories: {list(classifier.classes_)}")

if __name__ == "__main__":
    main()