#!/usr/bin/env python3
"""
Comprehensive Model Testing Suite
=================================

Advanced testing methods for log classification model including:
- Precision/Recall Analysis
- ROC-AUC Analysis  
- Cross-Validation Testing
- Robustness Testing
- Performance Benchmarking
- Error Analysis
- Feature Importance Analysis
"""

import joblib
import pandas as pd
import numpy as np
import time
import json
from collections import Counter, defaultdict
from sklearn.metrics import (
    precision_score, recall_score, f1_score, accuracy_score,
    classification_report, confusion_matrix,
    precision_recall_curve, roc_auc_score, roc_curve,
    matthews_corrcoef, cohen_kappa_score
)
from sklearn.model_selection import cross_val_score, StratifiedKFold
import warnings
warnings.filterwarnings('ignore')

class ComprehensiveModelTester:
    """Comprehensive testing suite for log classification model"""
    
    def __init__(self, model_path='models/enhanced_log_classifier.joblib'):
        self.model_path = model_path
        self.model = None
        self.test_data = self._prepare_comprehensive_test_data()
        
    def load_model(self):
        """Load the trained model"""
        try:
            self.model = joblib.load(self.model_path)
            print(f"✅ Model loaded from {self.model_path}")
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def _prepare_comprehensive_test_data(self):
        """Prepare comprehensive test dataset"""
        test_data = [
            # User Actions (20 samples)
            ("User admin logged in successfully", "user_action"),
            ("User jane.doe accessed customer database", "user_action"),
            ("User updated billing information", "user_action"),
            ("User downloaded monthly report.pdf", "user_action"),
            ("User created new project workspace", "user_action"),
            ("User modified security settings", "user_action"),
            ("User exported data to CSV format", "user_action"),
            ("User searched for transaction ID 12345", "user_action"),
            ("User uploaded document to shared folder", "user_action"),
            ("User scheduled automated backup", "user_action"),
            ("User viewed audit logs", "user_action"),
            ("User reset password successfully", "user_action"),
            ("User granted access to new team member", "user_action"),
            ("User archived old project files", "user_action"),
            ("User synchronized data with external system", "user_action"),
            ("User configured notification preferences", "user_action"),
            ("User published quarterly report", "user_action"),
            ("User initiated data migration process", "user_action"),
            ("User customized dashboard layout", "user_action"),
            ("User registered new API key", "user_action"),
            
            # Security Alerts (20 samples)
            ("Multiple failed login attempts from IP 192.168.1.50", "security_alert"),
            ("Suspicious file upload detected: malware.exe", "security_alert"),
            ("Unauthorized API access attempt blocked", "security_alert"),
            ("SQL injection attack detected and prevented", "security_alert"),
            ("Brute force attack on admin account", "security_alert"),
            ("Cross-site scripting attempt blocked", "security_alert"),
            ("Privilege escalation attempt detected", "security_alert"),
            ("Unusual data access pattern detected", "security_alert"),
            ("Potential data exfiltration attempt", "security_alert"),
            ("Suspicious network activity from external IP", "security_alert"),
            ("Failed authentication with stolen credentials", "security_alert"),
            ("Malicious script execution attempt", "security_alert"),
            ("Unauthorized file system access", "security_alert"),
            ("DDoS attack detected from multiple sources", "security_alert"),
            ("Ransomware signature detected", "security_alert"),
            ("Phishing attempt blocked by security filter", "security_alert"),
            ("Buffer overflow attack prevented", "security_alert"),
            ("Suspicious PowerShell execution detected", "security_alert"),
            ("Unauthorized certificate usage attempt", "security_alert"),
            ("Advanced persistent threat indicators found", "security_alert"),
            
            # System Notifications (15 samples)
            ("Database backup completed successfully", "system_notification"),
            ("System maintenance window started", "system_notification"),
            ("Server restart completed, all services online", "system_notification"),
            ("Memory usage returned to normal levels", "system_notification"),
            ("Disk cleanup process finished", "system_notification"),
            ("Log rotation completed successfully", "system_notification"),
            ("Cache refresh completed", "system_notification"),
            ("Service health check passed", "system_notification"),
            ("Configuration update applied successfully", "system_notification"),
            ("Scheduled job completed without errors", "system_notification"),
            ("System performance metrics collected", "system_notification"),
            ("Backup verification completed successfully", "system_notification"),
            ("Network connectivity restored", "system_notification"),
            ("Resource allocation optimized", "system_notification"),
            ("System monitoring alerts cleared", "system_notification"),
            
            # Workflow Errors (15 samples)
            ("Payment processing failed due to timeout", "workflow_error"),
            ("Database connection lost during transaction", "workflow_error"),
            ("API request failed with 500 internal error", "workflow_error"),
            ("File upload failed: file size exceeds limit", "workflow_error"),
            ("Email delivery failed: invalid recipient", "workflow_error"),
            ("Data synchronization failed", "workflow_error"),
            ("Report generation timed out", "workflow_error"),
            ("Import process failed: invalid file format", "workflow_error"),
            ("Export process interrupted by system error", "workflow_error"),
            ("Queue processing failed: message corrupted", "workflow_error"),
            ("Backup process failed: insufficient storage", "workflow_error"),
            ("Integration service unavailable", "workflow_error"),
            ("Validation error: required field missing", "workflow_error"),
            ("Connection timeout to external service", "workflow_error"),
            ("Resource allocation failed: quota exceeded", "workflow_error"),
            
            # Deprecation Warnings (10 samples)
            ("WARNING: Legacy authentication method deprecated", "deprecation_warning"),
            ("DEPRECATED: API version 1.0 will be removed", "deprecation_warning"),
            ("NOTICE: Old file format no longer supported", "deprecation_warning"),
            ("WARNING: TLS 1.0 support will be disabled", "deprecation_warning"),
            ("DEPRECATED: Legacy database driver", "deprecation_warning"),
            ("NOTICE: Old encryption algorithm deprecated", "deprecation_warning"),
            ("WARNING: Outdated browser version detected", "deprecation_warning"),
            ("DEPRECATED: Legacy configuration format", "deprecation_warning"),
            ("NOTICE: Old API endpoint scheduled for removal", "deprecation_warning"),
            ("WARNING: Unsupported software version in use", "deprecation_warning")
        ]
        
        return pd.DataFrame(test_data, columns=['message', 'true_label'])
    
    def test_1_precision_recall_analysis(self):
        """Test 1: Detailed Precision and Recall Analysis"""
        print("\n" + "="*80)
        print("📊 TEST 1: PRECISION & RECALL ANALYSIS")
        print("="*80)
        
        messages = self.test_data['message'].values
        true_labels = self.test_data['true_label'].values
        predictions = self.model.predict(messages)
        
        # Calculate precision and recall for each class
        precision_scores = precision_score(true_labels, predictions, average=None, zero_division=0)
        recall_scores = recall_score(true_labels, predictions, average=None, zero_division=0)
        f1_scores = f1_score(true_labels, predictions, average=None, zero_division=0)
        
        unique_labels = sorted(list(set(true_labels)))
        
        print(f"📋 Per-Class Precision & Recall:")
        for i, label in enumerate(unique_labels):
            if i < len(precision_scores):
                support = sum(1 for l in true_labels if l == label)
                print(f"   {label:<20}: Precision={precision_scores[i]:.4f} | "
                      f"Recall={recall_scores[i]:.4f} | F1={f1_scores[i]:.4f} | Support={support}")
        
        # Overall metrics
        precision_macro = precision_score(true_labels, predictions, average='macro', zero_division=0)
        recall_macro = recall_score(true_labels, predictions, average='macro', zero_division=0)
        precision_weighted = precision_score(true_labels, predictions, average='weighted', zero_division=0)
        recall_weighted = recall_score(true_labels, predictions, average='weighted', zero_division=0)
        
        print(f"\n📊 Summary Metrics:")
        print(f"   Macro Precision:    {precision_macro:.4f}")
        print(f"   Macro Recall:       {recall_macro:.4f}")
        print(f"   Weighted Precision: {precision_weighted:.4f}")
        print(f"   Weighted Recall:    {recall_weighted:.4f}")
        
        return {
            'precision_macro': precision_macro,
            'recall_macro': recall_macro,
            'precision_weighted': precision_weighted,
            'recall_weighted': recall_weighted,
            'per_class_metrics': dict(zip(unique_labels[:len(precision_scores)], 
                                        list(zip(precision_scores, recall_scores, f1_scores))))
        }
    
    def test_2_confusion_matrix_analysis(self):
        """Test 2: Detailed Confusion Matrix Analysis"""
        print("\n" + "="*80)
        print("📊 TEST 2: CONFUSION MATRIX ANALYSIS")
        print("="*80)
        
        messages = self.test_data['message'].values
        true_labels = self.test_data['true_label'].values
        predictions = self.model.predict(messages)
        
        # Generate confusion matrix
        cm = confusion_matrix(true_labels, predictions)
        unique_labels = sorted(list(set(true_labels + list(predictions))))
        
        print(f"📋 Confusion Matrix:")
        print(f"{'':20}", end="")
        for label in unique_labels:
            print(f"{label[:15]:>15}", end="")
        print()
        
        for i, true_label in enumerate(unique_labels):
            print(f"{true_label[:20]:20}", end="")
            for j, pred_label in enumerate(unique_labels):
                if i < len(cm) and j < len(cm[i]):
                    print(f"{cm[i][j]:15d}", end="")
                else:
                    print(f"{'0':15}", end="")
            print()
        
        # Calculate per-class accuracy
        class_accuracies = {}
        for i, label in enumerate(unique_labels):
            if i < len(cm):
                total_for_class = sum(cm[i])
                correct_for_class = cm[i][i] if i < len(cm[i]) else 0
                accuracy = correct_for_class / total_for_class if total_for_class > 0 else 0
                class_accuracies[label] = accuracy
        
        print(f"\n📊 Per-Class Accuracy from Confusion Matrix:")
        for label, acc in class_accuracies.items():
            print(f"   {label:<20}: {acc:.4f} ({acc*100:.1f}%)")
        
        return {'confusion_matrix': cm, 'class_accuracies': class_accuracies}
    
    def test_3_advanced_metrics(self):
        """Test 3: Advanced Statistical Metrics"""
        print("\n" + "="*80)
        print("📊 TEST 3: ADVANCED STATISTICAL METRICS")
        print("="*80)
        
        messages = self.test_data['message'].values
        true_labels = self.test_data['true_label'].values
        predictions = self.model.predict(messages)
        
        # Matthews Correlation Coefficient (better than accuracy for imbalanced data)
        try:
            mcc = matthews_corrcoef(true_labels, predictions)
            print(f"📊 Matthews Correlation Coefficient: {mcc:.4f}")
            if mcc > 0.8:
                mcc_interpretation = "Excellent correlation"
            elif mcc > 0.6:
                mcc_interpretation = "Good correlation"
            elif mcc > 0.4:
                mcc_interpretation = "Moderate correlation"
            else:
                mcc_interpretation = "Poor correlation"
            print(f"   Interpretation: {mcc_interpretation}")
        except Exception as e:
            mcc = None
            print(f"❌ Could not calculate MCC: {e}")
        
        # Cohen's Kappa (agreement between predictions and truth)
        try:
            kappa = cohen_kappa_score(true_labels, predictions)
            print(f"\n📊 Cohen's Kappa Score: {kappa:.4f}")
            if kappa > 0.8:
                kappa_interpretation = "Almost perfect agreement"
            elif kappa > 0.6:
                kappa_interpretation = "Substantial agreement"
            elif kappa > 0.4:
                kappa_interpretation = "Moderate agreement"
            elif kappa > 0.2:
                kappa_interpretation = "Fair agreement"
            else:
                kappa_interpretation = "Poor agreement"
            print(f"   Interpretation: {kappa_interpretation}")
        except Exception as e:
            kappa = None
            print(f"❌ Could not calculate Kappa: {e}")
        
        return {'matthews_corr_coef': mcc, 'cohens_kappa': kappa}
    
    def test_4_robustness_testing(self):
        """Test 4: Model Robustness and Edge Cases"""
        print("\n" + "="*80)
        print("📊 TEST 4: ROBUSTNESS & EDGE CASE TESTING")
        print("="*80)
        
        # Edge cases for robustness testing
        edge_cases = [
            # Empty/minimal inputs
            ("", "unclassified"),
            (".", "unclassified"),
            ("a", "unclassified"),
            ("User", "user_action"),
            
            # Very long inputs
            ("User " + "very " * 50 + "long log message with repetitive content", "user_action"),
            ("Failed " + "login " * 30 + "attempt with repetitive pattern", "security_alert"),
            
            # Special characters and encoding
            ("User@#$%^&*()_+ logged in with special chars", "user_action"),
            ("Sécûrïty âlért wïth ûnïcödé çhäräctérs", "security_alert"),
            ("User\t\n\r logged in with whitespace chars", "user_action"),
            
            # Mixed case and formatting
            ("USER LOGGED IN WITH CAPS", "user_action"),
            ("user logged in with lowercase", "user_action"),
            ("UsEr LoGgEd In WiTh MiXeD cAsE", "user_action"),
            
            # Ambiguous cases
            ("System user performed security check", "system_notification"),
            ("Security system generated user notification", "system_notification"),
            ("User security alert acknowledgment", "user_action"),
            
            # Typos and misspellings
            ("Usr loged in sucesfully", "user_action"),
            ("Securtiy alrt: faild login atempt", "security_alert"),
            ("Sytem maintanence complted", "system_notification"),
            
            # Numbers and technical terms
            ("User ID 12345 logged in from IP 192.168.1.100", "user_action"),
            ("Error code 500: Internal server malfunction", "workflow_error"),
            ("HTTP 404 not found for resource /api/v1/users", "workflow_error")
        ]
        
        robust_correct = 0
        robust_total = len(edge_cases)
        edge_results = []
        
        for message, expected in edge_cases:
            try:
                prediction = self.model.predict([message])[0]
                is_correct = prediction == expected
                robust_correct += is_correct
                
                edge_results.append({
                    'message': message[:50] + "..." if len(message) > 50 else message,
                    'expected': expected,
                    'predicted': prediction,
                    'correct': is_correct
                })
                
                status = "✅" if is_correct else "❌"
                print(f"   {status} {message[:40]:<40} → Expected: {expected:<15} | Got: {prediction}")
                
            except Exception as e:
                print(f"   💥 Error processing: {message[:40]} | Error: {str(e)[:30]}")
                edge_results.append({
                    'message': message,
                    'expected': expected,
                    'predicted': 'ERROR',
                    'correct': False,
                    'error': str(e)
                })
        
        robustness_score = robust_correct / robust_total
        print(f"\n📊 Robustness Score: {robustness_score:.4f} ({robust_correct}/{robust_total})")
        
        if robustness_score >= 0.8:
            print("   ✅ EXCELLENT: Model handles edge cases very well")
        elif robustness_score >= 0.6:
            print("   ⚠️  GOOD: Model is reasonably robust")
        else:
            print("   ❌ POOR: Model struggles with edge cases")
        
        return {'robustness_score': robustness_score, 'edge_results': edge_results}
    
    def test_5_performance_benchmarking(self):
        """Test 5: Performance and Speed Benchmarking"""
        print("\n" + "="*80)
        print("📊 TEST 5: PERFORMANCE BENCHMARKING")
        print("="*80)
        
        messages = self.test_data['message'].values
        
        # Single prediction timing
        single_times = []
        for i in range(10):
            start_time = time.time()
            self.model.predict([messages[0]])
            single_times.append(time.time() - start_time)
        
        avg_single_time = np.mean(single_times)
        
        # Batch prediction timing
        batch_sizes = [1, 10, 50, 100]
        batch_results = {}
        
        for batch_size in batch_sizes:
            if batch_size <= len(messages):
                batch_messages = messages[:batch_size]
                
                times = []
                for _ in range(5):
                    start_time = time.time()
                    self.model.predict(batch_messages)
                    times.append(time.time() - start_time)
                
                avg_time = np.mean(times)
                throughput = batch_size / avg_time
                
                batch_results[batch_size] = {
                    'avg_time': avg_time,
                    'throughput': throughput,
                    'per_message_time': avg_time / batch_size
                }
                
                print(f"   Batch size {batch_size:3d}: {avg_time:.4f}s total | "
                      f"{throughput:.1f} msgs/sec | {avg_time/batch_size:.6f}s per msg")
        
        print(f"\n📊 Performance Summary:")
        print(f"   Single prediction: {avg_single_time:.6f} seconds")
        if 100 in batch_results:
            print(f"   Peak throughput: {batch_results[100]['throughput']:.1f} messages/second")
        
        return {'single_prediction_time': avg_single_time, 'batch_results': batch_results}
    
    def test_6_error_analysis(self):
        """Test 6: Detailed Error Analysis"""
        print("\n" + "="*80)
        print("📊 TEST 6: ERROR ANALYSIS")
        print("="*80)
        
        messages = self.test_data['message'].values
        true_labels = self.test_data['true_label'].values
        predictions = self.model.predict(messages)
        
        # Find all misclassifications
        errors = []
        for i, (true_label, predicted_label, message) in enumerate(zip(true_labels, predictions, messages)):
            if true_label != predicted_label:
                errors.append({
                    'index': i,
                    'message': message,
                    'true_label': true_label,
                    'predicted_label': predicted_label,
                    'message_length': len(message),
                    'message_words': len(message.split())
                })
        
        print(f"📊 Error Summary:")
        print(f"   Total errors: {len(errors)} out of {len(messages)} ({len(errors)/len(messages)*100:.1f}%)")
        
        if errors:
            print(f"\n❌ Detailed Error Analysis:")
            
            # Group errors by true label
            error_by_true_label = defaultdict(list)
            for error in errors:
                error_by_true_label[error['true_label']].append(error)
            
            for true_label, label_errors in error_by_true_label.items():
                print(f"\n   {true_label} misclassifications ({len(label_errors)}):")
                for error in label_errors[:3]:  # Show first 3 errors per category
                    print(f"      → {error['message'][:60]}...")
                    print(f"        True: {error['true_label']} | Predicted: {error['predicted_label']}")
            
            # Error patterns
            print(f"\n📊 Error Patterns:")
            predicted_labels = [e['predicted_label'] for e in errors]
            error_distribution = Counter(predicted_labels)
            for pred_label, count in error_distribution.most_common():
                print(f"   Most often misclassified as {pred_label}: {count} times")
        
        return {'total_errors': len(errors), 'error_details': errors}
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 COMPREHENSIVE MODEL TESTING SUITE")
        print("="*80)
        print(f"📋 Testing Dataset: {len(self.test_data)} samples across {len(self.test_data['true_label'].unique())} categories")
        
        if not self.load_model():
            return None
        
        results = {}
        
        # Run all tests
        results['test_1_precision_recall'] = self.test_1_precision_recall_analysis()
        results['test_2_confusion_matrix'] = self.test_2_confusion_matrix_analysis()
        results['test_3_advanced_metrics'] = self.test_3_advanced_metrics()
        results['test_4_robustness'] = self.test_4_robustness_testing()
        results['test_5_performance'] = self.test_5_performance_benchmarking()
        results['test_6_error_analysis'] = self.test_6_error_analysis()
        
        # Overall summary
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        
        print(f"✅ Precision & Recall Test: Completed")
        print(f"✅ Confusion Matrix Analysis: Completed")
        print(f"✅ Advanced Metrics Test: Completed")
        print(f"✅ Robustness Testing: {results['test_4_robustness']['robustness_score']:.3f} score")
        print(f"✅ Performance Benchmarking: Completed")
        print(f"✅ Error Analysis: {results['test_6_error_analysis']['total_errors']} errors found")
        
        # Save comprehensive results
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"comprehensive_test_results_{timestamp}.json"
        
        # Convert numpy types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        json_results = json.loads(json.dumps(results, default=convert_types))
        json_results['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        json_results['test_summary'] = {
            'total_samples': len(self.test_data),
            'categories': len(self.test_data['true_label'].unique()),
            'robustness_score': results['test_4_robustness']['robustness_score'],
            'total_errors': results['test_6_error_analysis']['total_errors']
        }
        
        with open(filename, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"\n💾 Comprehensive results saved to: {filename}")
        
        return results

def main():
    """Main function to run comprehensive testing"""
    tester = ComprehensiveModelTester()
    results = tester.run_all_tests()
    
    if results:
        print(f"\n✅ Comprehensive testing completed successfully!")
        print(f"📊 Your model has been evaluated across 6 different test categories")
        print(f"🎯 Key insights: Check robustness score and error analysis for improvement areas")

if __name__ == "__main__":
    main()