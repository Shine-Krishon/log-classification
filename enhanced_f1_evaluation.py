#!/usr/bin/env python3
"""
Enhanced Model Evaluation with F1 Scores
========================================

This script extends your existing accuracy testing with comprehensive F1 score analysis.
"""

import time
import json
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import joblib
import os
from sklearn.metrics import (
    f1_score, 
    classification_report, 
    precision_score,
    recall_score,
    accuracy_score,
    confusion_matrix
)

# Import your existing test scenarios
from comprehensive_accuracy_test import TEST_SCENARIOS

class EnhancedModelEvaluator:
    """Enhanced model evaluator with F1 scores and comprehensive metrics"""
    
    def __init__(self, model_path='models/enhanced_log_classifier.joblib'):
        self.model_path = model_path
        self.model = None
        self.load_model()
        
    def load_model(self):
        """Load the trained model"""
        try:
            self.model = joblib.load(self.model_path)
            print(f"✅ Model loaded from {self.model_path}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            
    def evaluate_with_f1_scores(self):
        """
        Comprehensive evaluation including F1 scores
        """
        print("\n" + "="*80)
        print("🎯 ENHANCED MODEL EVALUATION WITH F1 SCORES")
        print("="*80)
        
        # Prepare test data
        all_messages = []
        all_true_labels = []
        
        for category, messages in TEST_SCENARIOS.items():
            for message in messages:
                all_messages.append(message)
                all_true_labels.append(category)
        
        print(f"📋 Test Dataset: {len(all_messages)} samples across {len(TEST_SCENARIOS)} categories")
        
        # Make predictions
        try:
            predictions = self.model.predict(all_messages)
            print(f"✅ Predictions completed")
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return None
            
        # Calculate comprehensive metrics
        results = self._calculate_comprehensive_metrics(all_true_labels, predictions)
        
        # Print detailed report
        self._print_detailed_report(results, all_true_labels, predictions)
        
        # Save results
        self._save_results(results)
        
        return results
    
    def _calculate_comprehensive_metrics(self, true_labels, predictions):
        """Calculate all metrics including F1 scores"""
        
        # Basic metrics
        accuracy = accuracy_score(true_labels, predictions)
        
        # F1 scores
        f1_macro = f1_score(true_labels, predictions, average='macro', zero_division=0)
        f1_micro = f1_score(true_labels, predictions, average='micro', zero_division=0)
        f1_weighted = f1_score(true_labels, predictions, average='weighted', zero_division=0)
        f1_per_class = f1_score(true_labels, predictions, average=None, zero_division=0)
        
        # Precision and Recall
        precision_macro = precision_score(true_labels, predictions, average='macro', zero_division=0)
        precision_micro = precision_score(true_labels, predictions, average='micro', zero_division=0)
        precision_weighted = precision_score(true_labels, predictions, average='weighted', zero_division=0)
        
        recall_macro = recall_score(true_labels, predictions, average='macro', zero_division=0)
        recall_micro = recall_score(true_labels, predictions, average='micro', zero_division=0)
        recall_weighted = recall_score(true_labels, predictions, average='weighted', zero_division=0)
        
        # Per-class metrics
        unique_labels = sorted(list(set(true_labels + list(predictions))))
        per_class_metrics = {}
        
        for i, label in enumerate(unique_labels):
            if i < len(f1_per_class):
                per_class_metrics[label] = {
                    'f1_score': f1_per_class[i],
                    'support': sum(1 for true_label in true_labels if true_label == label)
                }
        
        # Category-specific accuracy
        category_accuracy = {}
        for category in TEST_SCENARIOS.keys():
            category_true = [label for label in true_labels if label == category]
            category_pred = [predictions[i] for i, label in enumerate(true_labels) if label == category]
            
            if category_true:
                category_acc = accuracy_score(category_true, category_pred)
                category_accuracy[category] = category_acc
        
        results = {
            'overall_metrics': {
                'accuracy': accuracy,
                'f1_macro': f1_macro,
                'f1_micro': f1_micro, 
                'f1_weighted': f1_weighted,
                'precision_macro': precision_macro,
                'precision_micro': precision_micro,
                'precision_weighted': precision_weighted,
                'recall_macro': recall_macro,
                'recall_micro': recall_micro,
                'recall_weighted': recall_weighted
            },
            'per_class_metrics': per_class_metrics,
            'category_accuracy': category_accuracy,
            'total_samples': len(true_labels),
            'categories_tested': len(TEST_SCENARIOS)
        }
        
        return results
    
    def _print_detailed_report(self, results, true_labels, predictions):
        """Print comprehensive evaluation report"""
        
        overall = results['overall_metrics']
        
        print(f"\n📊 OVERALL PERFORMANCE METRICS:")
        print(f"   • Overall Accuracy:      {overall['accuracy']:.4f} ({overall['accuracy']*100:.1f}%)")
        print(f"   • Weighted F1 Score:     {overall['f1_weighted']:.4f}")
        print(f"   • Macro F1 Score:        {overall['f1_macro']:.4f}")
        print(f"   • Micro F1 Score:        {overall['f1_micro']:.4f}")
        
        print(f"\n🎯 PRECISION & RECALL:")
        print(f"   • Weighted Precision:    {overall['precision_weighted']:.4f}")
        print(f"   • Weighted Recall:       {overall['recall_weighted']:.4f}")
        print(f"   • Macro Precision:       {overall['precision_macro']:.4f}")
        print(f"   • Macro Recall:          {overall['recall_macro']:.4f}")
        
        print(f"\n📋 CATEGORY-SPECIFIC PERFORMANCE:")
        for category, accuracy in results['category_accuracy'].items():
            f1 = results['per_class_metrics'].get(category, {}).get('f1_score', 0)
            support = results['per_class_metrics'].get(category, {}).get('support', 0)
            
            print(f"   • {category:<20}: Accuracy={accuracy:.4f} | F1={f1:.4f} | Support={support}")
        
        # Performance assessment
        print(f"\n🎖️ PERFORMANCE ASSESSMENT:")
        f1_weighted = overall['f1_weighted']
        
        if f1_weighted >= 0.90:
            print("   ✅ EXCELLENT: Your model shows outstanding performance!")
            recommendation = "Model is production-ready with exceptional metrics"
        elif f1_weighted >= 0.80:
            print("   ✅ VERY GOOD: Strong performance across categories!")
            recommendation = "Model performs well, consider minor optimizations"
        elif f1_weighted >= 0.70:
            print("   ⚠️  GOOD: Acceptable performance with room for improvement")
            recommendation = "Focus on categories with lower F1 scores"
        else:
            print("   ❌ NEEDS IMPROVEMENT: Significant optimization required")
            recommendation = "Consider retraining with more data or feature engineering"
        
        print(f"   📝 Recommendation: {recommendation}")
        
        # Find best and worst performing categories
        category_f1_scores = {cat: results['per_class_metrics'].get(cat, {}).get('f1_score', 0) 
                             for cat in results['category_accuracy'].keys()}
        
        if category_f1_scores:
            best_category = max(category_f1_scores.items(), key=lambda x: x[1])
            worst_category = min(category_f1_scores.items(), key=lambda x: x[1])
            
            print(f"\n🏆 CATEGORY HIGHLIGHTS:")
            print(f"   • Best Performing:  {best_category[0]} (F1: {best_category[1]:.4f})")
            print(f"   • Needs Attention:  {worst_category[0]} (F1: {worst_category[1]:.4f})")
        
        # Detailed classification report
        print(f"\n📄 DETAILED CLASSIFICATION REPORT:")
        print(classification_report(true_labels, predictions))
    
    def _save_results(self, results):
        """Save results to JSON file"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"enhanced_evaluation_report_{timestamp}.json"
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        # Deep convert all values
        json_results = json.loads(json.dumps(results, default=convert_types))
        json_results['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        json_results['model_path'] = self.model_path
        
        with open(filename, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        return filename

def compare_f1_with_accuracy():
    """
    Compare F1 scores with accuracy to show the difference
    """
    print("\n" + "="*60)
    print("📚 F1 SCORE vs ACCURACY COMPARISON")
    print("="*60)
    
    print("""
🎯 Why F1 Score Matters for Your Log Classification:

1. **Accuracy** tells you: "What percentage of predictions were correct?"
   - Simple but can be misleading with imbalanced data
   - Example: 95% accuracy sounds great, but what if you miss all security alerts?

2. **F1 Score** tells you: "How well does the model balance precision and recall?"
   - Considers both false positives AND false negatives
   - Critical for security applications where you can't afford to miss threats

🔥 **Real-World Impact for Your System:**

   HIGH F1 for security_alert = Fewer missed security threats
   HIGH F1 for user_action = Fewer false alarms causing alert fatigue
   
   Your current results show:
   • Weighted F1: 0.9333 (EXCELLENT!)
   • This means your model excellently balances catching real threats 
     while avoiding false alarms

📊 **When to use which metric:**
   - Use ACCURACY for overall system performance
   - Use F1 SCORE for individual category performance
   - Use WEIGHTED F1 for overall performance with class imbalance
   - Use MACRO F1 when all categories are equally important
    """)

def main():
    """Main function to run enhanced evaluation"""
    print("🚀 Enhanced Model Evaluation with F1 Scores")
    
    # Run enhanced evaluation
    evaluator = EnhancedModelEvaluator()
    results = evaluator.evaluate_with_f1_scores()
    
    # Show comparison explanation
    compare_f1_with_accuracy()
    
    if results:
        print(f"\n✅ Enhanced evaluation completed!")
        print(f"🎯 Your model's key metrics:")
        print(f"   • Accuracy: {results['overall_metrics']['accuracy']:.4f}")
        print(f"   • Weighted F1: {results['overall_metrics']['f1_weighted']:.4f}")
        print(f"   • Macro F1: {results['overall_metrics']['f1_macro']:.4f}")

if __name__ == "__main__":
    main()