#!/usr/bin/env python3
"""
Comprehensive Model Accuracy Testing Suite
Performs extensive testing on the current log classification model
"""

import time
import json
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import requests
import os

# Test categories and expected results
TEST_SCENARIOS = {
    "user_actions": [
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
    "security_alerts": [
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
    "system_notifications": [
        "System backup completed successfully",
        "Database maintenance scheduled for tonight",
        "Server restart required for updates",
        "Disk space warning: 85% full",
        "Service restart completed",
        "Configuration updated successfully",
        "Cache cleared automatically",
        "Log rotation completed",
        "Certificate renewal reminder",
        "System health check passed"
    ],
    "workflow_errors": [
        "Payment processing failed for order #12345",
        "Email delivery failed: invalid address",
        "File upload failed: size limit exceeded",
        "Database connection timeout",
        "API request failed: rate limit exceeded",
        "Report generation failed: insufficient data",
        "Backup failed: storage unavailable",
        "Import process failed: format error",
        "Sync operation failed: network error",
        "Task execution failed: permission denied"
    ],
    "deprecation_warnings": [
        "DEPRECATED: Function old_auth() will be removed in v2.0",
        "WARNING: Legacy API endpoint /v1/users is deprecated",
        "NOTICE: Old configuration format no longer supported",
        "DEPRECATED: Database driver version 1.x is obsolete",
        "WARNING: SSL protocol TLS 1.0 is deprecated",
        "NOTICE: PHP version 7.x support ending soon",
        "DEPRECATED: jQuery version 1.x is no longer maintained",
        "WARNING: Python 2.7 support has ended",
        "NOTICE: Old encryption method will be disabled",
        "DEPRECATED: Legacy file format no longer supported"
    ]
}

def test_direct_classification():
    """Test direct classification using enhanced_production_system"""
    print("="*80)
    print("🔬 DIRECT CLASSIFICATION TESTING")
    print("="*80)
    
    try:
        from enhanced_production_system import classify_log_message
        
        results = {}
        total_correct = 0
        total_tests = 0
        
        for category, messages in TEST_SCENARIOS.items():
            print(f"\n📝 Testing {category.upper()}:")
            print("-" * 50)
            
            category_correct = 0
            category_total = len(messages)
            category_results = []
            
            for message in messages:
                try:
                    result = classify_log_message(message)
                    predicted = result.get('prediction', 'unknown')
                    confidence = result.get('confidence', 0.0)
                    
                    # Map category names for comparison
                    expected_category = category.rstrip('s')  # Remove plural 's'
                    if expected_category == 'user_action':
                        expected_category = 'user_action'
                    elif expected_category == 'security_alert':
                        expected_category = 'security_alert'
                    elif expected_category == 'system_notification':
                        expected_category = 'system_notification'
                    elif expected_category == 'workflow_error':
                        expected_category = 'workflow_error'
                    elif expected_category == 'deprecation_warning':
                        expected_category = 'deprecation_warning'
                    
                    is_correct = predicted == expected_category
                    category_correct += is_correct
                    total_correct += is_correct
                    total_tests += 1
                    
                    status = "✅" if is_correct else "❌"
                    print(f"{status} '{message[:60]}...' → {predicted} (conf: {confidence:.2f})")
                    
                    category_results.append({
                        'message': message,
                        'expected': expected_category,
                        'predicted': predicted,
                        'confidence': confidence,
                        'correct': is_correct
                    })
                    
                except Exception as e:
                    print(f"❌ ERROR: {message[:60]}... → {e}")
                    total_tests += 1
            
            category_accuracy = category_correct / category_total if category_total > 0 else 0
            print(f"\n📊 {category.upper()} Accuracy: {category_accuracy:.1%} ({category_correct}/{category_total})")
            
            results[category] = {
                'accuracy': category_accuracy,
                'correct': category_correct,
                'total': category_total,
                'results': category_results
            }
        
        overall_accuracy = total_correct / total_tests if total_tests > 0 else 0
        print(f"\n🎯 OVERALL DIRECT CLASSIFICATION ACCURACY: {overall_accuracy:.1%} ({total_correct}/{total_tests})")
        
        return results, overall_accuracy
        
    except Exception as e:
        print(f"❌ Direct classification test failed: {e}")
        return {}, 0.0

def test_api_classification():
    """Test classification via API endpoint"""
    print("\n" + "="*80)
    print("🌐 API CLASSIFICATION TESTING")
    print("="*80)
    
    try:
        # Create comprehensive test CSV
        test_data = []
        for category, messages in TEST_SCENARIOS.items():
            for message in messages[:5]:  # Test 5 from each category
                test_data.append({
                    'source': 'test_system',
                    'log_message': message,
                    'expected_category': category.rstrip('s')
                })
        
        # Save to CSV
        df = pd.DataFrame(test_data)
        csv_file = "comprehensive_api_test.csv"
        df[['source', 'log_message']].to_csv(csv_file, index=False)
        
        print(f"📄 Created test file with {len(test_data)} log entries")
        
        # Test API
        with open(csv_file, 'rb') as f:
            files = {'file': (csv_file, f, 'text/csv')}
            response = requests.post(
                "http://localhost:8000/api/v1/classify/",
                files=files,
                timeout=60
            )
        
        if response.status_code == 200:
            result = response.json()
            classified_logs = result.get('classified_logs', [])
            
            print(f"✅ API processed {len(classified_logs)} logs")
            print(f"⏱️ Processing time: {result.get('processing_time_seconds', 0):.2f} seconds")
            
            # Calculate accuracy by category
            api_results = {}
            total_correct = 0
            total_tests = len(classified_logs)
            
            for i, log_entry in enumerate(classified_logs):
                if i < len(test_data):
                    expected = test_data[i]['expected_category']
                    if expected == 'user_action':
                        expected = 'user_action'
                    elif expected == 'security_alert':
                        expected = 'security_alert'
                    elif expected == 'system_notification':
                        expected = 'system_notification'
                    elif expected == 'workflow_error':
                        expected = 'workflow_error'
                    elif expected == 'deprecation_warning':
                        expected = 'deprecation_warning'
                    
                    predicted = log_entry.get('target_label', 'unknown')
                    is_correct = predicted == expected
                    total_correct += is_correct
                    
                    status = "✅" if is_correct else "❌"
                    message = log_entry.get('log_message', '')
                    print(f"{status} '{message[:50]}...' → {predicted} (expected: {expected})")
            
            api_accuracy = total_correct / total_tests if total_tests > 0 else 0
            print(f"\n🎯 API OVERALL ACCURACY: {api_accuracy:.1%} ({total_correct}/{total_tests})")
            
            # Show processing stats
            processing_stats = result.get('processing_stats', {})
            print(f"\n📈 Processing Distribution:")
            for method, count in processing_stats.items():
                percentage = (count / total_tests * 100) if total_tests > 0 else 0
                print(f"   • {method}: {count} logs ({percentage:.1f}%)")
            
            return api_accuracy, processing_stats
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return 0.0, {}
            
    except Exception as e:
        print(f"❌ API classification test failed: {e}")
        return 0.0, {}

def test_edge_cases():
    """Test edge cases and unusual inputs"""
    print("\n" + "="*80)
    print("🎭 EDGE CASE TESTING")
    print("="*80)
    
    edge_cases = [
        ("", "Empty string"),
        ("   ", "Whitespace only"),
        ("a", "Single character"),
        ("User" * 100, "Very long repetitive text"),
        ("🔥💻🚨 User logged in with emojis 🎉", "Text with emojis"),
        ("ADMIN USER LOGGED IN WITH CAPS", "All caps text"),
        ("user 123 logged in lowercase", "All lowercase"),
        ("User-123_logged@in#with$special%chars", "Special characters"),
        ("Benutzer 12345 hat sich angemeldet", "Non-English (German)"),
        ("Usuario 12345 inició sesión", "Non-English (Spanish)"),
        ("SELECT * FROM users WHERE password=''; DROP TABLE users;--", "SQL injection attempt in log"),
        ("<script>alert('xss')</script> User logged in", "XSS attempt in log"),
        ("User logged in at " + "2025-01-01 " * 50, "Very long timestamp"),
        ("NULL", "NULL string"),
        ("undefined", "Undefined string"),
        ("NaN", "NaN string")
    ]
    
    try:
        from enhanced_production_system import classify_log_message
        
        edge_results = []
        successful_classifications = 0
        
        for test_input, description in edge_cases:
            try:
                result = classify_log_message(test_input)
                predicted = result.get('prediction', 'unknown')
                confidence = result.get('confidence', 0.0)
                
                successful_classifications += 1
                status = "✅"
                
                print(f"{status} {description}: '{test_input[:40]}...' → {predicted} (conf: {confidence:.2f})")
                
                edge_results.append({
                    'input': test_input,
                    'description': description,
                    'predicted': predicted,
                    'confidence': confidence,
                    'success': True
                })
                
            except Exception as e:
                print(f"❌ {description}: ERROR - {e}")
                edge_results.append({
                    'input': test_input,
                    'description': description,
                    'error': str(e),
                    'success': False
                })
        
        edge_robustness = successful_classifications / len(edge_cases)
        print(f"\n🛡️ EDGE CASE ROBUSTNESS: {edge_robustness:.1%} ({successful_classifications}/{len(edge_cases)})")
        
        return edge_robustness, edge_results
        
    except Exception as e:
        print(f"❌ Edge case testing failed: {e}")
        return 0.0, []

def generate_performance_report():
    """Generate comprehensive performance report"""
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE PERFORMANCE REPORT")
    print("="*80)
    
    # Run all tests
    direct_results, direct_accuracy = test_direct_classification()
    api_accuracy, processing_stats = test_api_classification()
    edge_robustness, edge_results = test_edge_cases()
    
    # Calculate weighted average accuracy
    weights = {'direct': 0.5, 'api': 0.3, 'edge': 0.2}
    weighted_accuracy = (
        direct_accuracy * weights['direct'] +
        api_accuracy * weights['api'] +
        edge_robustness * weights['edge']
    )
    
    # Generate report
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'model_path': 'models/enhanced_log_classifier.joblib',
        'model_type': 'SVM Pipeline (TF-IDF + SVC)',
        'overall_metrics': {
            'weighted_accuracy': weighted_accuracy,
            'direct_classification_accuracy': direct_accuracy,
            'api_accuracy': api_accuracy,
            'edge_case_robustness': edge_robustness
        },
        'category_breakdown': direct_results,
        'processing_distribution': processing_stats,
        'edge_case_results': edge_results,
        'test_coverage': {
            'total_scenarios': sum(len(messages) for messages in TEST_SCENARIOS.values()),
            'categories_tested': len(TEST_SCENARIOS),
            'edge_cases_tested': len(edge_results)
        }
    }
    
    # Save report
    with open('model_performance_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n🎯 FINAL ACCURACY METRICS:")
    print(f"   • Overall Weighted Accuracy: {weighted_accuracy:.1%}")
    print(f"   • Direct Classification: {direct_accuracy:.1%}")
    print(f"   • API Classification: {api_accuracy:.1%}")
    print(f"   • Edge Case Robustness: {edge_robustness:.1%}")
    
    print(f"\n📄 Detailed report saved to: model_performance_report.json")
    
    return report

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Model Accuracy Testing...")
    report = generate_performance_report()
    print("\n✅ Testing complete!")