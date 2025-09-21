#!/usr/bin/env python3
"""
F1 Score Evaluation for Log Classification Model
===============================================

This script provides comprehensive F1 score analysis for the log classification model,
including overall F1, category-specific F1, macro/micro averages, and detailed metrics.
"""

import pandas as pd
import numpy as np
import joblib
import json
from sklearn.metrics import (
    f1_score, 
    classification_report, 
    confusion_matrix,
    precision_recall_fscore_support,
    accuracy_score
)
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Test data for evaluation
TEST_DATA = {
    "user_action": [
        "User 12345 logged in",
        "User john.doe logged out", 
        "User accessed dashboard page",
        "User uploaded file report.pdf",
        "User updated profile information",
        "User searched for 'sales data'",
        "User created new record ID: 789",
        "User deleted old backup file",
        "User generated monthly report",
        "User changed password successfully",
        "User downloaded quarterly report",
        "User modified account settings",
        "User viewed customer details",
        "User exported data to CSV",
        "User sent email notification"
    ],
    "security_alert": [
        "Failed login attempt from IP 192.168.1.100",
        "Multiple failed login attempts detected",
        "Suspicious activity: brute force attack", 
        "Unauthorized access attempt blocked",
        "SQL injection attempt detected",
        "Cross-site scripting attack prevented",
        "Malware detected in uploaded file",
        "Privilege escalation attempt blocked",
        "Data exfiltration attempt detected",
        "Session hijacking attempt prevented",
        "DDoS attack detected from multiple IPs",
        "Phishing attempt blocked",
        "Buffer overflow attack detected",
        "Port scanning activity detected",
        "Ransomware signature detected"
    ],
    "system_notification": [
        "Database backup completed successfully",
        "System maintenance scheduled for tonight",
        "Server restart completed",
        "Cache cleared successfully",
        "Configuration updated",
        "Service health check passed",
        "Disk cleanup completed",
        "Log rotation performed",
        "Memory usage normal",
        "CPU utilization stable"
    ],
    "workflow_error": [
        "Payment processing failed",
        "Database connection timeout",
        "API request failed with 500 error",
        "File upload failed - size too large",
        "Email delivery failed",
        "Backup process encountered error",
        "Import process failed - invalid format",
        "Export timeout exceeded",
        "Service unavailable",
        "Queue processing error"
    ],
    "deprecation_warning": [
        "WARNING: Legacy API will be deprecated in v2.0",
        "DEPRECATED: Function xyz() will be removed",
        "NOTICE: Old encryption method will be disabled",
        "DEPRECATED: Legacy file format no longer supported",
        "WARNING: This feature will be removed in next version",
        "NOTICE: Update required for continued support",
        "DEPRECATED: Old authentication method",
        "WARNING: SSL version deprecated",
        "NOTICE: Database schema change required",
        "DEPRECATED: Legacy report format"
    ]
}

class F1ScoreEvaluator:
    """Comprehensive F1 Score Evaluation for Log Classification Model"""
    
    def __init__(self, model_path='models/enhanced_log_classifier.joblib'):
        """Initialize the evaluator with the trained model"""
        self.model_path = model_path
        self.model = None
        self.test_data = self._prepare_test_data()
        self.predictions = None
        self.true_labels = None
        
    def load_model(self):
        """Load the trained model"""
        try:
            self.model = joblib.load(self.model_path)
            print(f"✅ Model loaded successfully from {self.model_path}")
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def _prepare_test_data(self):
        """Prepare test data from the test scenarios"""
        data = []
        for category, messages in TEST_DATA.items():
            for message in messages:
                data.append({
                    'log_message': message,
                    'true_label': category
                })
        return pd.DataFrame(data)
    
    def make_predictions(self):
        """Make predictions on test data"""
        if self.model is None:
            print("❌ Model not loaded")
            return False
            
        try:
            self.predictions = self.model.predict(self.test_data['log_message'])
            self.true_labels = self.test_data['true_label'].values
            print(f"✅ Predictions completed for {len(self.test_data)} samples")
            return True
        except Exception as e:
            print(f"❌ Error making predictions: {e}")
            return False
    
    def calculate_f1_scores(self):
        """Calculate comprehensive F1 scores"""
        if self.predictions is None or self.true_labels is None:
            print("❌ No predictions available")
            return None
            
        # Calculate different F1 score variants
        f1_macro = f1_score(self.true_labels, self.predictions, average='macro')
        f1_micro = f1_score(self.true_labels, self.predictions, average='micro')  
        f1_weighted = f1_score(self.true_labels, self.predictions, average='weighted')
        
        # Per-class F1 scores
        f1_per_class = f1_score(self.true_labels, self.predictions, average=None)
        
        # Get unique labels
        unique_labels = sorted(list(set(self.true_labels) | set(self.predictions)))
        
        # Create per-class F1 dictionary
        f1_per_class_dict = {}
        for i, label in enumerate(unique_labels):
            if i < len(f1_per_class):
                f1_per_class_dict[label] = f1_per_class[i]
        
        results = {
            'f1_macro': f1_macro,
            'f1_micro': f1_micro,
            'f1_weighted': f1_weighted,
            'f1_per_class': f1_per_class_dict,
            'unique_labels': unique_labels
        }
        
        return results
    
    def get_detailed_metrics(self):
        """Get detailed classification metrics including precision and recall"""
        if self.predictions is None or self.true_labels is None:
            return None
            
        # Get classification report as dictionary
        report = classification_report(
            self.true_labels, 
            self.predictions, 
            output_dict=True,
            zero_division=0
        )
        
        # Calculate accuracy
        accuracy = accuracy_score(self.true_labels, self.predictions)
        
        # Get precision, recall, f1 for each class
        precision, recall, f1, support = precision_recall_fscore_support(
            self.true_labels, 
            self.predictions, 
            average=None,
            zero_division=0
        )
        
        # Get unique labels
        unique_labels = sorted(list(set(self.true_labels) | set(self.predictions)))
        
        detailed_metrics = {
            'accuracy': accuracy,
            'classification_report': report,
            'per_class_metrics': {}
        }
        
        for i, label in enumerate(unique_labels):
            if i < len(precision):
                detailed_metrics['per_class_metrics'][label] = {
                    'precision': precision[i],
                    'recall': recall[i],
                    'f1_score': f1[i],
                    'support': support[i] if i < len(support) else 0
                }
        
        return detailed_metrics
    
    def generate_confusion_matrix(self, save_plot=True):
        """Generate and optionally save confusion matrix"""
        if self.predictions is None or self.true_labels is None:
            return None
            
        # Create confusion matrix
        cm = confusion_matrix(self.true_labels, self.predictions)
        unique_labels = sorted(list(set(self.true_labels) | set(self.predictions)))
        
        if save_plot:
            plt.figure(figsize=(10, 8))
            sns.heatmap(
                cm, 
                annot=True, 
                fmt='d', 
                cmap='Blues',
                xticklabels=unique_labels,
                yticklabels=unique_labels
            )
            plt.title('Confusion Matrix - Log Classification Model')
            plt.xlabel('Predicted Label')
            plt.ylabel('True Label')
            plt.xticks(rotation=45)
            plt.yticks(rotation=0)
            plt.tight_layout()
            plt.savefig('confusion_matrix_f1_evaluation.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("📊 Confusion matrix saved as 'confusion_matrix_f1_evaluation.png'")
        
        return cm, unique_labels
    
    def create_f1_visualization(self):
        """Create F1 score visualization"""
        f1_results = self.calculate_f1_scores()
        if not f1_results:
            return
            
        # Create F1 score bar chart
        plt.figure(figsize=(12, 8))
        
        # Plot per-class F1 scores
        categories = list(f1_results['f1_per_class'].keys())
        f1_scores = list(f1_results['f1_per_class'].values())
        
        bars = plt.bar(categories, f1_scores, color='skyblue', alpha=0.7)
        
        # Add value labels on bars
        for bar, score in zip(bars, f1_scores):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # Add horizontal lines for macro, micro, weighted averages
        plt.axhline(y=f1_results['f1_macro'], color='red', linestyle='--', 
                   label=f'Macro F1: {f1_results["f1_macro"]:.3f}')
        plt.axhline(y=f1_results['f1_micro'], color='green', linestyle='--',
                   label=f'Micro F1: {f1_results["f1_micro"]:.3f}')
        plt.axhline(y=f1_results['f1_weighted'], color='orange', linestyle='--',
                   label=f'Weighted F1: {f1_results["f1_weighted"]:.3f}')
        
        plt.title('F1 Scores by Category - Log Classification Model', fontsize=14, fontweight='bold')
        plt.xlabel('Log Categories', fontsize=12)
        plt.ylabel('F1 Score', fontsize=12)
        plt.xticks(rotation=45)
        plt.ylim(0, 1.1)
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig('f1_scores_by_category.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("📊 F1 score visualization saved as 'f1_scores_by_category.png'")
    
    def print_comprehensive_report(self):
        """Print comprehensive F1 score report"""
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE F1 SCORE EVALUATION REPORT")
        print("="*80)
        
        # Calculate F1 scores
        f1_results = self.calculate_f1_scores()
        detailed_metrics = self.get_detailed_metrics()
        
        if not f1_results or not detailed_metrics:
            print("❌ Unable to generate report")
            return
        
        print(f"\n📊 OVERALL F1 SCORE METRICS:")
        print(f"   • Macro F1 Score:    {f1_results['f1_macro']:.4f}")
        print(f"   • Micro F1 Score:    {f1_results['f1_micro']:.4f}")  
        print(f"   • Weighted F1 Score: {f1_results['f1_weighted']:.4f}")
        print(f"   • Overall Accuracy:  {detailed_metrics['accuracy']:.4f}")
        
        print(f"\n📋 CATEGORY-SPECIFIC F1 SCORES:")
        for category, f1 in f1_results['f1_per_class'].items():
            if category in detailed_metrics['per_class_metrics']:
                metrics = detailed_metrics['per_class_metrics'][category]
                print(f"   • {category:<20}: F1={f1:.4f} | "
                     f"Precision={metrics['precision']:.4f} | "
                     f"Recall={metrics['recall']:.4f} | "
                     f"Support={metrics['support']}")
        
        print(f"\n🎖️ F1 SCORE INTERPRETATION:")
        if f1_results['f1_weighted'] >= 0.90:
            print("   ✅ EXCELLENT: F1 score indicates outstanding model performance")
        elif f1_results['f1_weighted'] >= 0.80:
            print("   ✅ VERY GOOD: F1 score indicates strong model performance")
        elif f1_results['f1_weighted'] >= 0.70:
            print("   ⚠️  GOOD: F1 score indicates acceptable model performance")
        elif f1_results['f1_weighted'] >= 0.60:
            print("   ⚠️  FAIR: F1 score indicates room for improvement")
        else:
            print("   ❌ POOR: F1 score indicates significant improvement needed")
        
        # Find best and worst performing categories
        f1_scores = f1_results['f1_per_class']
        if f1_scores:
            best_category = max(f1_scores.items(), key=lambda x: x[1])
            worst_category = min(f1_scores.items(), key=lambda x: x[1])
            
            print(f"\n🏆 PERFORMANCE HIGHLIGHTS:")
            print(f"   • Best Category:  {best_category[0]} (F1: {best_category[1]:.4f})")
            print(f"   • Worst Category: {worst_category[0]} (F1: {worst_category[1]:.4f})")
        
        # Model information
        print(f"\n🔧 MODEL INFORMATION:")
        print(f"   • Model Path: {self.model_path}")
        print(f"   • Test Samples: {len(self.test_data)}")
        print(f"   • Categories: {len(f1_results['unique_labels'])}")
        print(f"   • Evaluation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return f1_results, detailed_metrics
    
    def save_results_to_file(self, f1_results, detailed_metrics):
        """Save F1 score results to JSON file"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'model_path': self.model_path,
            'f1_scores': {
                'macro': float(f1_results['f1_macro']),
                'micro': float(f1_results['f1_micro']),
                'weighted': float(f1_results['f1_weighted']),
                'per_class': {k: float(v) for k, v in f1_results['f1_per_class'].items()}
            },
            'accuracy': float(detailed_metrics['accuracy']),
            'detailed_metrics': {
                k: {
                    'precision': float(v['precision']),
                    'recall': float(v['recall']),
                    'f1_score': float(v['f1_score']),
                    'support': int(v['support'])
                } for k, v in detailed_metrics['per_class_metrics'].items()
            },
            'test_summary': {
                'total_samples': len(self.test_data),
                'categories_tested': len(f1_results['unique_labels']),
                'samples_per_category': dict(self.test_data['true_label'].value_counts())
            }
        }
        
        filename = f"f1_score_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"💾 F1 score report saved to '{filename}'")
        return filename

def main():
    """Main function to run F1 score evaluation"""
    print("🚀 Starting F1 Score Evaluation for Log Classification Model...")
    
    # Initialize evaluator
    evaluator = F1ScoreEvaluator()
    
    # Load model
    if not evaluator.load_model():
        return
    
    # Make predictions
    if not evaluator.make_predictions():
        return
    
    # Generate comprehensive report
    f1_results, detailed_metrics = evaluator.print_comprehensive_report()
    
    # Create visualizations
    evaluator.generate_confusion_matrix()
    evaluator.create_f1_visualization()
    
    # Save results
    evaluator.save_results_to_file(f1_results, detailed_metrics)
    
    print("\n✅ F1 Score Evaluation Complete!")
    print("\nGenerated Files:")
    print("   📊 confusion_matrix_f1_evaluation.png")
    print("   📊 f1_scores_by_category.png") 
    print("   💾 f1_score_report_[timestamp].json")

if __name__ == "__main__":
    main()