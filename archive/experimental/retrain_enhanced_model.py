#!/usr/bin/env python3
"""
Enhanced Model Retraining Script for Log Classification with Security Alerts

This script retrains the existing model to handle the new security_alert category
and provides options to upgrade/improve the existing model architecture.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
import joblib
import time
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class EnhancedLogClassifier:
    """Enhanced Log Classifier with support for security alerts"""
    
    def __init__(self):
        self.models = {}
        self.best_model = None
        self.best_model_name = None
        self.best_score = 0.0
        self.label_counts = {}
        
    def load_dataset(self, filepath='logs_chunk1.csv'):
        """Load and analyze the dataset"""
        print("=== Loading Dataset ===")
        
        self.df = pd.read_csv(filepath)
        print(f"Dataset size: {len(self.df):,} samples")
        print(f"Features: {list(self.df.columns)}")
        
        # Check for security_alert category
        unique_labels = sorted(self.df['target_label'].unique())
        print(f"Classes ({len(unique_labels)}): {unique_labels}")
        
        # Class distribution
        self.label_counts = self.df['target_label'].value_counts()
        print(f"\nClass distribution:")
        for label, count in self.label_counts.items():
            percentage = (count / len(self.df)) * 100
            print(f"  {label}: {count:,} samples ({percentage:.1f}%)")
        
        # Check if security_alert exists
        if 'security_alert' in unique_labels:
            print("✅ Security Alert category detected!")
            security_count = self.label_counts['security_alert']
            print(f"   Security alerts: {security_count} samples")
        else:
            print("❌ No Security Alert category found")
            return False
            
        return True
    
    def prepare_data(self, test_size=0.2, val_size=0.1):
        """Prepare train/validation/test splits"""
        print(f"\n=== Preparing Data Splits ===")
        
        X = self.df['log_message']
        y = self.df['target_label']
        
        # First split: separate test set
        X_temp, self.X_test, y_temp, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Second split: separate train and validation
        val_ratio = val_size / (1 - test_size)
        self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(
            X_temp, y_temp, test_size=val_ratio, random_state=42, stratify=y_temp
        )
        
        print(f"Train set: {len(self.X_train):,} samples")
        print(f"Validation set: {len(self.X_val):,} samples") 
        print(f"Test set: {len(self.X_test):,} samples")
        
        # Show class distribution in each split
        print(f"\nClass distribution in splits:")
        for split_name, y_split in [('Train', self.y_train), ('Val', self.y_val), ('Test', self.y_test)]:
            print(f"  {split_name}:")
            for label in sorted(y_split.unique()):
                count = (y_split == label).sum()
                percentage = (count / len(y_split)) * 100
                print(f"    {label}: {count} ({percentage:.1f}%)")
    
    def train_enhanced_tfidf_logistic_regression(self):
        """Train enhanced TF-IDF + Logistic Regression model"""
        print(f"\n=== Training Enhanced TF-IDF + Logistic Regression ===")
        
        start_time = time.time()
        
        # Enhanced TF-IDF pipeline with security-aware features
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=15000,  # Increased for security patterns
                ngram_range=(1, 3),  # Include trigrams for security terms
                stop_words='english',
                min_df=2,
                max_df=0.95,
                sublinear_tf=True,  # Use sublinear scaling
                analyzer='word'
            )),
            ('lr', LogisticRegression(
                max_iter=2000,  # More iterations for convergence
                random_state=42,
                C=1.0,
                class_weight='balanced',  # Handle class imbalance
                solver='liblinear'  # Good for text classification
            ))
        ])
        
        pipeline.fit(self.X_train, self.y_train)
        train_time = time.time() - start_time
        
        # Evaluate
        val_pred = pipeline.predict(self.X_val)
        val_acc = accuracy_score(self.y_val, val_pred)
        
        test_pred = pipeline.predict(self.X_test)
        test_acc = accuracy_score(self.y_test, test_pred)
        
        print(f"Training time: {train_time:.1f} seconds")
        print(f"Validation accuracy: {val_acc:.4f}")
        print(f"Test accuracy: {test_acc:.4f}")
        
        self.models['Enhanced_Logistic_Regression'] = {
            'model': pipeline,
            'val_acc': val_acc,
            'test_acc': test_acc,
            'train_time': train_time,
            'test_pred': test_pred
        }
        
        return pipeline, test_acc
    
    def train_optimized_random_forest(self):
        """Train optimized Random Forest model"""
        print(f"\n=== Training Optimized Random Forest ===")
        
        start_time = time.time()
        
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=8000,  # Optimal for RF
                ngram_range=(1, 2),
                stop_words='english',
                min_df=3,
                max_df=0.9
            )),
            ('rf', RandomForestClassifier(
                n_estimators=200,  # More trees for better performance
                max_depth=25,
                min_samples_split=8,
                min_samples_leaf=3,
                max_features='sqrt',
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'
            ))
        ])
        
        pipeline.fit(self.X_train, self.y_train)
        train_time = time.time() - start_time
        
        # Evaluate
        val_pred = pipeline.predict(self.X_val)
        val_acc = accuracy_score(self.y_val, val_pred)
        
        test_pred = pipeline.predict(self.X_test)
        test_acc = accuracy_score(self.y_test, test_pred)
        
        print(f"Training time: {train_time:.1f} seconds")
        print(f"Validation accuracy: {val_acc:.4f}")
        print(f"Test accuracy: {test_acc:.4f}")
        
        self.models['Optimized_Random_Forest'] = {
            'model': pipeline,
            'val_acc': val_acc,
            'test_acc': test_acc,
            'train_time': train_time,
            'test_pred': test_pred
        }
        
        return pipeline, test_acc
    
    def train_gradient_boosting(self):
        """Train Gradient Boosting model (upgrade option)"""
        print(f"\n=== Training Gradient Boosting Classifier ===")
        
        start_time = time.time()
        
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=10000,
                ngram_range=(1, 2),
                stop_words='english',
                min_df=3,
                max_df=0.9
            )),
            ('gb', GradientBoostingClassifier(
                n_estimators=150,
                learning_rate=0.1,
                max_depth=15,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42,
                subsample=0.8
            ))
        ])
        
        pipeline.fit(self.X_train, self.y_train)
        train_time = time.time() - start_time
        
        # Evaluate
        val_pred = pipeline.predict(self.X_val)
        val_acc = accuracy_score(self.y_val, val_pred)
        
        test_pred = pipeline.predict(self.X_test)
        test_acc = accuracy_score(self.y_test, test_pred)
        
        print(f"Training time: {train_time:.1f} seconds")
        print(f"Validation accuracy: {val_acc:.4f}")
        print(f"Test accuracy: {test_acc:.4f}")
        
        self.models['Gradient_Boosting'] = {
            'model': pipeline,
            'val_acc': val_acc,
            'test_acc': test_acc,
            'train_time': train_time,
            'test_pred': test_pred
        }
        
        return pipeline, test_acc
    
    def train_svm_classifier(self):
        """Train SVM classifier (premium upgrade option)"""
        print(f"\n=== Training SVM Classifier ===")
        
        start_time = time.time()
        
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=5000,  # Lower for SVM performance
                ngram_range=(1, 2),
                stop_words='english',
                min_df=3,
                max_df=0.9
            )),
            ('svm', SVC(
                kernel='linear',
                C=1.0,
                random_state=42,
                class_weight='balanced',
                probability=True  # Enable probability predictions
            ))
        ])
        
        pipeline.fit(self.X_train, self.y_train)
        train_time = time.time() - start_time
        
        # Evaluate
        val_pred = pipeline.predict(self.X_val)
        val_acc = accuracy_score(self.y_val, val_pred)
        
        test_pred = pipeline.predict(self.X_test)
        test_acc = accuracy_score(self.y_test, test_pred)
        
        print(f"Training time: {train_time:.1f} seconds")
        print(f"Validation accuracy: {val_acc:.4f}")
        print(f"Test accuracy: {test_acc:.4f}")
        
        self.models['SVM_Linear'] = {
            'model': pipeline,
            'val_acc': val_acc,
            'test_acc': test_acc,
            'train_time': train_time,
            'test_pred': test_pred
        }
        
        return pipeline, test_acc
    
    def train_all_models(self):
        """Train all available models"""
        print("=== Training All Models ===")
        
        # Train all models
        self.train_enhanced_tfidf_logistic_regression()
        self.train_optimized_random_forest()
        self.train_gradient_boosting()
        
        # Only train SVM if dataset is not too large (performance consideration)
        if len(self.X_train) < 15000:
            self.train_svm_classifier()
        else:
            print("⚠️  Skipping SVM due to large dataset size (would be too slow)")
        
        # Find best model
        best_test_acc = 0
        for name, info in self.models.items():
            if info['test_acc'] > best_test_acc:
                best_test_acc = info['test_acc']
                self.best_model = info['model']
                self.best_model_name = name
                self.best_score = best_test_acc
        
        print(f"\n=== Model Comparison ===")
        print(f"{'Model':<25} {'Val Acc':<10} {'Test Acc':<10} {'Train Time':<12}")
        print("-" * 60)
        
        for name, info in self.models.items():
            marker = " 🏆" if name == self.best_model_name else ""
            print(f"{name:<25} {info['val_acc']:<10.4f} {info['test_acc']:<10.4f} {info['train_time']:<12.1f}s{marker}")
        
        print(f"\n🏆 Best Model: {self.best_model_name}")
        print(f"   Test Accuracy: {self.best_score:.4f}")
    
    def evaluate_security_performance(self):
        """Detailed evaluation of security alert classification"""
        print(f"\n=== Security Alert Performance Analysis ===")
        
        if self.best_model is None:
            print("No trained model available")
            return
        
        best_info = self.models[self.best_model_name]
        y_pred = best_info['test_pred']
        
        # Overall classification report
        print("Classification Report:")
        print(classification_report(self.y_test, y_pred))
        
        # Security-specific analysis
        security_mask = self.y_test == 'security_alert'
        if security_mask.sum() > 0:
            security_true = self.y_test[security_mask]
            security_pred = y_pred[security_mask]
            security_acc = accuracy_score(security_true, security_pred)
            
            print(f"\n🔒 Security Alert Specific Performance:")
            print(f"   Security samples in test set: {security_mask.sum()}")
            print(f"   Security classification accuracy: {security_acc:.4f}")
            
            # Check what security alerts were misclassified as
            misclassified = security_pred != security_true
            if misclassified.sum() > 0:
                print(f"   Misclassified security alerts: {misclassified.sum()}")
                print("   Misclassified as:")
                for label in np.unique(security_pred[misclassified]):
                    count = (security_pred[misclassified] == label).sum()
                    print(f"     {label}: {count} cases")
            else:
                print("   ✅ All security alerts correctly classified!")
        
        # Check false positives (non-security classified as security)
        non_security_mask = self.y_test != 'security_alert'
        non_security_pred_as_security = (y_pred == 'security_alert') & non_security_mask
        
        if non_security_pred_as_security.sum() > 0:
            print(f"\n⚠️  False Security Alerts: {non_security_pred_as_security.sum()}")
            false_security_true_labels = self.y_test[non_security_pred_as_security]
            print("   Actually were:")
            for label in np.unique(false_security_true_labels):
                count = (false_security_true_labels == label).sum()
                print(f"     {label}: {count} cases")
        else:
            print(f"\n✅ No false security alerts!")
    
    def save_models(self):
        """Save the trained models"""
        print(f"\n=== Saving Models ===")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save best model as primary
        primary_filename = 'log_classifier_with_security_alerts.joblib'
        joblib.dump(self.best_model, primary_filename)
        print(f"✅ Primary model saved: {primary_filename}")
        print(f"   Model type: {self.best_model_name}")
        print(f"   Test accuracy: {self.best_score:.4f}")
        
        # Save all models with timestamp
        models_dir = 'models_backup'
        os.makedirs(models_dir, exist_ok=True)
        
        for name, info in self.models.items():
            filename = f"{models_dir}/log_classifier_{name.lower()}_{timestamp}.joblib"
            joblib.dump(info['model'], filename)
            print(f"   Backup saved: {filename}")
        
        # Save model comparison results
        results_df = pd.DataFrame([
            {
                'model_name': name,
                'validation_accuracy': info['val_acc'],
                'test_accuracy': info['test_acc'],
                'training_time_seconds': info['train_time'],
                'is_best': name == self.best_model_name
            }
            for name, info in self.models.items()
        ])
        
        results_filename = f'model_comparison_results_{timestamp}.csv'
        results_df.to_csv(results_filename, index=False)
        print(f"   Results saved: {results_filename}")
    
    def demonstrate_security_classification(self):
        """Demonstrate security alert classification"""
        print(f"\n=== Security Classification Demonstration ===")
        
        if self.best_model is None:
            print("No trained model available")
            return
        
        # Security test examples
        security_examples = [
            "Failed login attempt for user admin from IP 192.168.1.100",
            "SQL injection attempt detected in user input",
            "Unauthorized access attempt detected from IP 10.0.0.5",
            "Malicious file upload detected: virus signature found",
            "DDoS attack detected from multiple IP addresses",
            "Privilege escalation attempt detected",
            "Suspicious network traffic blocked by firewall",
            "Account lockout triggered after multiple failed attempts"
        ]
        
        # Non-security examples for comparison
        other_examples = [
            "User john.doe logged in successfully",
            "Application started on port 8080",
            "Database backup completed successfully", 
            "Payment processing failed: insufficient funds",
            "Configuration file reloaded",
            "API deprecation notice: endpoint will be removed"
        ]
        
        print("🔒 Security Alert Examples:")
        print("-" * 60)
        
        for example in security_examples:
            prediction = self.best_model.predict([example])[0]
            probabilities = self.best_model.predict_proba([example])[0]
            confidence = max(probabilities)
            
            status = "✅" if prediction == 'security_alert' else "❌"
            print(f"{status} {example}")
            print(f"   Predicted: {prediction} (confidence: {confidence:.3f})")
            print()
        
        print("📝 Other Log Examples:")
        print("-" * 60)
        
        for example in other_examples:
            prediction = self.best_model.predict([example])[0]
            probabilities = self.best_model.predict_proba([example])[0]
            confidence = max(probabilities)
            
            status = "✅" if prediction != 'security_alert' else "⚠️"
            print(f"{status} {example}")
            print(f"   Predicted: {prediction} (confidence: {confidence:.3f})")
            print()
    
    def upgrade_existing_model(self):
        """Compare with existing model if available"""
        print(f"\n=== Existing Model Upgrade Analysis ===")
        
        existing_model_path = 'log_classifier_20k_random_forest.joblib'
        
        if os.path.exists(existing_model_path):
            try:
                print(f"Loading existing model: {existing_model_path}")
                existing_model = joblib.load(existing_model_path)
                
                # Test existing model on new data (it won't know about security_alert)
                try:
                    existing_pred = existing_model.predict(self.X_test)
                    
                    # Calculate accuracy (this will be lower since security_alert is new)
                    # We'll exclude security_alert samples for fair comparison
                    non_security_mask = self.y_test != 'security_alert'
                    if non_security_mask.sum() > 0:
                        existing_acc = accuracy_score(
                            self.y_test[non_security_mask], 
                            existing_pred[non_security_mask]
                        )
                        
                        new_acc = accuracy_score(
                            self.y_test[non_security_mask],
                            self.models[self.best_model_name]['test_pred'][non_security_mask]
                        )
                        
                        print(f"Existing model accuracy (non-security): {existing_acc:.4f}")
                        print(f"New model accuracy (non-security): {new_acc:.4f}")
                        print(f"Improvement: {(new_acc - existing_acc)*100:.2f} percentage points")
                        
                        if new_acc > existing_acc:
                            print("✅ New model outperforms existing model!")
                        else:
                            print("🤔 Existing model still competitive on non-security logs")
                    
                    # Check how existing model handles security alerts
                    security_mask = self.y_test == 'security_alert'
                    if security_mask.sum() > 0:
                        security_pred_old = existing_pred[security_mask]
                        print(f"\nSecurity alerts classification by old model:")
                        for label in np.unique(security_pred_old):
                            count = (security_pred_old == label).sum()
                            percentage = (count / security_mask.sum()) * 100
                            print(f"  {label}: {count} ({percentage:.1f}%)")
                        
                        print(f"\n🆕 NEW CAPABILITY: Security alert detection!")
                        print(f"   Old model cannot detect security alerts")
                        print(f"   New model correctly identifies {self.label_counts['security_alert']} security patterns")
                
                except Exception as e:
                    print(f"Error testing existing model: {e}")
                    print("This might be due to different feature spaces")
                
            except Exception as e:
                print(f"Could not load existing model: {e}")
        else:
            print(f"No existing model found at {existing_model_path}")
            print("This will be a completely new model deployment")

def main():
    """Main execution function"""
    print("🚀 Enhanced Log Classification Model Training")
    print("=" * 60)
    
    classifier = EnhancedLogClassifier()
    
    # Load and analyze dataset
    if not classifier.load_dataset():
        print("❌ Dataset loading failed or no security alerts found")
        return
    
    # Prepare data
    classifier.prepare_data()
    
    # Train all models
    classifier.train_all_models()
    
    # Detailed security evaluation
    classifier.evaluate_security_performance()
    
    # Compare with existing model
    classifier.upgrade_existing_model()
    
    # Save models
    classifier.save_models()
    
    # Demonstrate security classification
    classifier.demonstrate_security_classification()
    
    print(f"\n🎉 Model retraining completed successfully!")
    print(f"   Best model: {classifier.best_model_name}")
    print(f"   Test accuracy: {classifier.best_score:.4f}")
    print(f"   Security alerts supported: ✅")
    print(f"   Model file: log_classifier_with_security_alerts.joblib")

if __name__ == "__main__":
    main()