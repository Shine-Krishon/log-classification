#!/usr/bin/env python3
"""
Additional Specialized Model Tests
=================================

Extra testing methods beyond basic accuracy/F1:
- Cross-Validation Testing
- Learning Curve Analysis  
- Feature Importance Analysis
- Stress Testing
- Bias Detection
- Drift Detection Simulation
"""

import joblib
import pandas as pd
import numpy as np
import time
from sklearn.model_selection import cross_val_score, StratifiedKFold, learning_curve
from sklearn.metrics import accuracy_score, f1_score, classification_report
from collections import Counter, defaultdict
import json

class SpecializedModelTests:
    """Additional specialized tests for model evaluation"""
    
    def __init__(self, model_path='models/enhanced_log_classifier.joblib'):
        self.model_path = model_path
        self.model = None
        self.load_model()
        
    def load_model(self):
        """Load the trained model"""
        try:
            self.model = joblib.load(self.model_path)
            print(f"✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
    
    def test_7_cross_validation(self):
        """Test 7: Cross-Validation Analysis"""
        print("\n" + "="*80)
        print("📊 TEST 7: CROSS-VALIDATION ANALYSIS")
        print("="*80)
        
        # Prepare dataset for cross-validation
        test_data = self._get_cv_dataset()
        X = test_data['message'].values
        y = test_data['true_label'].values
        
        print(f"📋 Cross-validation with {len(X)} samples")
        
        # Perform k-fold cross-validation
        cv_folds = [3, 5, 10]
        cv_results = {}
        
        for k in cv_folds:
            if k <= len(set(y)):  # Ensure we have enough samples per class
                try:
                    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=42)
                    cv_scores = cross_val_score(self.model, X, y, cv=skf, scoring='accuracy')
                    
                    cv_results[f'{k}_fold'] = {
                        'scores': cv_scores.tolist(),
                        'mean': cv_scores.mean(),
                        'std': cv_scores.std(),
                        'min': cv_scores.min(),
                        'max': cv_scores.max()
                    }
                    
                    print(f"   {k}-Fold CV: {cv_scores.mean():.4f} ± {cv_scores.std():.4f} "
                          f"(min: {cv_scores.min():.4f}, max: {cv_scores.max():.4f})")
                    
                except Exception as e:
                    print(f"   ❌ {k}-Fold CV failed: {e}")
        
        # Variance analysis
        if cv_results:
            best_k = min(cv_results.keys(), key=lambda k: cv_results[k]['std'])
            print(f"\n📊 Most stable performance: {best_k} (lowest variance)")
            
            if cv_results[best_k]['std'] < 0.05:
                print("   ✅ EXCELLENT: Very consistent performance across folds")
            elif cv_results[best_k]['std'] < 0.1:
                print("   ⚠️  GOOD: Reasonably consistent performance")
            else:
                print("   ❌ POOR: High variance - model may be unstable")
        
        return cv_results
    
    def test_8_stress_testing(self):
        """Test 8: Stress Testing with High Volume"""
        print("\n" + "="*80)
        print("📊 TEST 8: STRESS TESTING")
        print("="*80)
        
        # Generate stress test data
        base_messages = [
            "User logged in successfully",
            "Failed login attempt detected", 
            "System backup completed",
            "Payment processing failed",
            "WARNING: Legacy API deprecated"
        ]
        
        stress_results = {}
        
        # Test with increasing volume
        volumes = [100, 500, 1000, 5000]
        
        for volume in volumes:
            print(f"\n   Testing with {volume} messages...")
            
            # Create test dataset
            messages = []
            for i in range(volume):
                base_msg = base_messages[i % len(base_messages)]
                messages.append(f"{base_msg} - instance {i}")
            
            # Measure performance
            start_time = time.time()
            try:
                predictions = self.model.predict(messages)
                end_time = time.time()
                
                total_time = end_time - start_time
                throughput = volume / total_time
                avg_time_per_msg = total_time / volume
                
                stress_results[volume] = {
                    'total_time': total_time,
                    'throughput': throughput,
                    'avg_time_per_message': avg_time_per_msg,
                    'success': True
                }
                
                print(f"      ✅ Processed {volume} messages in {total_time:.3f}s")
                print(f"      📊 Throughput: {throughput:.1f} messages/second")
                print(f"      ⏱️  Average: {avg_time_per_msg:.6f}s per message")
                
            except Exception as e:
                stress_results[volume] = {
                    'error': str(e),
                    'success': False
                }
                print(f"      ❌ Failed to process {volume} messages: {e}")
        
        # Performance degradation analysis
        successful_tests = {k: v for k, v in stress_results.items() if v.get('success', False)}
        if len(successful_tests) > 1:
            throughputs = [v['throughput'] for v in successful_tests.values()]
            if max(throughputs) / min(throughputs) > 2:
                print(f"\n   ⚠️  WARNING: Performance degrades significantly with volume")
            else:
                print(f"\n   ✅ Performance scales well with volume")
        
        return stress_results
    
    def test_9_bias_detection(self):
        """Test 9: Bias Detection in Classifications"""
        print("\n" + "="*80)
        print("📊 TEST 9: BIAS DETECTION ANALYSIS")
        print("="*80)
        
        # Test for potential biases in classification
        bias_tests = [
            # Length bias
            {
                'name': 'Length Bias Test',
                'short_msgs': [
                    "User login",
                    "Failed auth", 
                    "Backup done",
                    "Error 500",
                    "API deprecated"
                ],
                'long_msgs': [
                    "User authentication process completed successfully with multi-factor verification and session establishment",
                    "Failed authentication attempt detected from external IP address with multiple retry patterns indicating potential security threat",
                    "System backup process completed successfully with all data verified and stored in secure backup location",
                    "Internal server error 500 occurred during processing of user request due to database connection timeout",
                    "Legacy API endpoint deprecated and scheduled for removal in next major version release"
                ]
            },
            # Time-related bias
            {
                'name': 'Time Pattern Bias Test',
                'time_msgs': [
                    "User logged in at 09:00 AM",
                    "User logged in at 02:00 AM", 
                    "Failed login at 15:30 PM",
                    "Failed login at 03:45 AM",
                    "System backup at 12:00 PM",
                    "System backup at 23:30 PM"
                ]
            },
            # Keyword sensitivity bias
            {
                'name': 'Keyword Sensitivity Test',
                'keyword_msgs': [
                    "User admin logged in",
                    "User guest logged in",
                    "User root logged in",
                    "Security admin alert",
                    "Security user alert",
                    "Security guest alert"
                ]
            }
        ]
        
        bias_results = {}
        
        for test in bias_tests:
            test_name = test['name']
            print(f"\n   {test_name}:")
            
            if 'short_msgs' in test and 'long_msgs' in test:
                # Length bias test
                short_preds = self.model.predict(test['short_msgs'])
                long_preds = self.model.predict(test['long_msgs'])
                
                short_distribution = Counter(short_preds)
                long_distribution = Counter(long_preds)
                
                print(f"      Short messages: {dict(short_distribution)}")
                print(f"      Long messages:  {dict(long_distribution)}")
                
                # Check if distributions are significantly different
                short_security = short_distribution.get('security_alert', 0) / len(short_preds)
                long_security = long_distribution.get('security_alert', 0) / len(long_preds)
                
                if abs(short_security - long_security) > 0.3:
                    print(f"      ⚠️  Potential length bias detected")
                else:
                    print(f"      ✅ No significant length bias")
                
                bias_results[test_name] = {
                    'short_distribution': dict(short_distribution),
                    'long_distribution': dict(long_distribution),
                    'bias_detected': abs(short_security - long_security) > 0.3
                }
            
            elif 'time_msgs' in test:
                # Time pattern bias test
                time_preds = self.model.predict(test['time_msgs'])
                time_distribution = Counter(time_preds)
                print(f"      Time pattern results: {dict(time_distribution)}")
                
                bias_results[test_name] = {
                    'distribution': dict(time_distribution)
                }
            
            elif 'keyword_msgs' in test:
                # Keyword sensitivity test
                keyword_preds = self.model.predict(test['keyword_msgs'])
                keyword_distribution = Counter(keyword_preds)
                print(f"      Keyword sensitivity: {dict(keyword_distribution)}")
                
                bias_results[test_name] = {
                    'distribution': dict(keyword_distribution)
                }
        
        return bias_results
    
    def test_10_concept_drift_simulation(self):
        """Test 10: Concept Drift Detection Simulation"""
        print("\n" + "="*80)
        print("📊 TEST 10: CONCEPT DRIFT SIMULATION")
        print("="*80)
        
        # Simulate concept drift by creating different "time periods"
        periods = {
            'baseline': [
                ("User logged in", "user_action"),
                ("Failed login attempt", "security_alert"),
                ("Database backup completed", "system_notification"),
                ("Payment failed", "workflow_error"),
                ("API deprecated", "deprecation_warning")
            ],
            'period_1': [
                ("User authenticated via SSO", "user_action"),
                ("Suspicious login pattern detected", "security_alert"), 
                ("Cloud backup synchronized", "system_notification"),
                ("Transaction timeout", "workflow_error"),
                ("Legacy endpoint sunset", "deprecation_warning")
            ],
            'period_2': [
                ("User accessed via mobile app", "user_action"),
                ("Anomalous behavior detected", "security_alert"),
                ("Microservice health check", "system_notification"), 
                ("API rate limit exceeded", "workflow_error"),
                ("Service version deprecated", "deprecation_warning")
            ]
        }
        
        drift_results = {}
        
        for period_name, period_data in periods.items():
            messages = [item[0] for item in period_data]
            true_labels = [item[1] for item in period_data]
            
            predictions = self.model.predict(messages)
            accuracy = accuracy_score(true_labels, predictions)
            f1 = f1_score(true_labels, predictions, average='weighted', zero_division=0)
            
            drift_results[period_name] = {
                'accuracy': accuracy,
                'f1_score': f1,
                'predictions': predictions.tolist(),
                'true_labels': true_labels
            }
            
            print(f"   {period_name}: Accuracy={accuracy:.4f}, F1={f1:.4f}")
        
        # Detect performance drift
        baseline_acc = drift_results['baseline']['accuracy']
        
        print(f"\n📊 Drift Analysis:")
        for period in ['period_1', 'period_2']:
            if period in drift_results:
                current_acc = drift_results[period]['accuracy']
                drift_amount = abs(baseline_acc - current_acc)
                
                if drift_amount > 0.1:
                    status = "🚨 SIGNIFICANT DRIFT"
                elif drift_amount > 0.05:
                    status = "⚠️  MODERATE DRIFT"
                else:
                    status = "✅ STABLE"
                
                print(f"   {period}: {status} (Δ={drift_amount:.4f})")
        
        return drift_results
    
    def test_11_confidence_analysis(self):
        """Test 11: Prediction Confidence Analysis"""
        print("\n" + "="*80)
        print("📊 TEST 11: PREDICTION CONFIDENCE ANALYSIS")
        print("="*80)
        
        # Test messages with varying confidence levels
        confidence_test_messages = [
            "User logged in successfully",  # Should be high confidence
            "Failed login attempt detected",  # Should be high confidence
            "User security system notification",  # Ambiguous - lower confidence
            "Error failed user",  # Very ambiguous
            "System user security failed login backup"  # Very confusing
        ]
        
        print("📊 Analyzing prediction confidence...")
        
        # Check if model has predict_proba method
        confidence_results = {}
        
        if hasattr(self.model, 'predict_proba'):
            try:
                probabilities = self.model.predict_proba(confidence_test_messages)
                predictions = self.model.predict(confidence_test_messages)
                
                for i, (msg, pred, probs) in enumerate(zip(confidence_test_messages, predictions, probabilities)):
                    max_prob = np.max(probs)
                    confidence_level = "High" if max_prob > 0.8 else "Medium" if max_prob > 0.6 else "Low"
                    
                    print(f"   Message: {msg[:50]}...")
                    print(f"      Prediction: {pred} (Confidence: {max_prob:.4f} - {confidence_level})")
                    
                    confidence_results[f'message_{i}'] = {
                        'message': msg,
                        'prediction': pred,
                        'max_probability': max_prob,
                        'confidence_level': confidence_level,
                        'all_probabilities': probs.tolist()
                    }
                    
            except Exception as e:
                print(f"   ❌ Could not analyze confidence: {e}")
                confidence_results['error'] = str(e)
        else:
            # Use decision function if available
            if hasattr(self.model, 'decision_function'):
                try:
                    decisions = self.model.decision_function(confidence_test_messages)
                    predictions = self.model.predict(confidence_test_messages)
                    
                    for i, (msg, pred, decision) in enumerate(zip(confidence_test_messages, predictions, decisions)):
                        # For multi-class, take max decision value
                        max_decision = np.max(decision) if isinstance(decision, np.ndarray) else decision
                        confidence_level = "High" if max_decision > 1.0 else "Medium" if max_decision > 0 else "Low"
                        
                        print(f"   Message: {msg[:50]}...")
                        print(f"      Prediction: {pred} (Decision: {max_decision:.4f} - {confidence_level})")
                        
                        confidence_results[f'message_{i}'] = {
                            'message': msg,
                            'prediction': pred,
                            'decision_value': max_decision,
                            'confidence_level': confidence_level
                        }
                        
                except Exception as e:
                    print(f"   ❌ Could not analyze decision function: {e}")
                    confidence_results['error'] = str(e)
            else:
                print("   ⚠️  Model does not support confidence analysis")
                confidence_results['support'] = False
        
        return confidence_results
    
    def _get_cv_dataset(self):
        """Get dataset for cross-validation"""
        data = [
            ("User logged in", "user_action"),
            ("User logged out", "user_action"),
            ("User accessed dashboard", "user_action"),
            ("Failed login attempt", "security_alert"),
            ("Suspicious activity detected", "security_alert"),
            ("Malware detected", "security_alert"),
            ("Backup completed", "system_notification"),
            ("System restarted", "system_notification"),
            ("Maintenance scheduled", "system_notification"),
            ("Payment failed", "workflow_error"),
            ("Connection timeout", "workflow_error"),
            ("Process failed", "workflow_error"),
            ("API deprecated", "deprecation_warning"),
            ("Legacy function removed", "deprecation_warning"),
            ("Old version unsupported", "deprecation_warning")
        ]
        return pd.DataFrame(data, columns=['message', 'true_label'])
    
    def run_specialized_tests(self):
        """Run all specialized tests"""
        print("🚀 SPECIALIZED MODEL TESTING SUITE")
        print("="*80)
        
        if not self.model:
            print("❌ Model not loaded")
            return None
        
        results = {}
        
        # Run specialized tests
        results['test_7_cross_validation'] = self.test_7_cross_validation()
        results['test_8_stress_testing'] = self.test_8_stress_testing()
        results['test_9_bias_detection'] = self.test_9_bias_detection()
        results['test_10_concept_drift'] = self.test_10_concept_drift_simulation()
        results['test_11_confidence_analysis'] = self.test_11_confidence_analysis()
        
        # Save results
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"specialized_test_results_{timestamp}.json"
        
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
        
        with open(filename, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"\n💾 Specialized test results saved to: {filename}")
        print(f"\n✅ All specialized tests completed!")
        
        return results

def main():
    """Main function"""
    tester = SpecializedModelTests()
    results = tester.run_specialized_tests()

if __name__ == "__main__":
    main()