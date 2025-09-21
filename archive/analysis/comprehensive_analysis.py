import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.processors.processor_regex import classify_with_regex

def comprehensive_misclassification_analysis():
    """Comprehensive analysis to find all potential misclassification issues."""
    
    print("🔍 COMPREHENSIVE MISCLASSIFICATION ANALYSIS")
    print("=" * 80)
    
    # 1. Analyze the test results first
    print("1. ANALYZING CURRENT TEST RESULTS")
    print("-" * 50)
    
    try:
        results_df = pd.read_csv('resources/output.csv')
        test_df = pd.read_csv('tests/test_data/medium_test.csv')
        
        print(f"Loaded {len(results_df)} classification results")
        print(f"Loaded {len(test_df)} test messages")
        
        # Merge to get source context
        merged_df = pd.merge(test_df, results_df, on=['source', 'log_message'], how='inner')
        print(f"Successfully merged {len(merged_df)} entries")
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    # 2. Analyze by source system
    print("\n2. ANALYSIS BY SOURCE SYSTEM")
    print("-" * 50)
    
    sources = merged_df['source'].unique()
    problematic_sources = []
    
    for source in sources:
        source_data = merged_df[merged_df['source'] == source]
        classifications = source_data['target_label'].value_counts()
        
        print(f"\n{source} ({len(source_data)} messages):")
        
        # Check for suspicious patterns
        security_pct = (classifications.get('security_alert', 0) / len(source_data)) * 100
        unclassified_pct = (classifications.get('unclassified', 0) / len(source_data)) * 100
        
        for label, count in classifications.items():
            pct = (count / len(source_data)) * 100
            print(f"  {label}: {count} ({pct:.1f}%)")
        
        # Flag problematic sources
        if security_pct > 40:  # More than 40% security alerts is suspicious
            problematic_sources.append((source, 'Too many security alerts', security_pct))
        if unclassified_pct > 20:  # More than 20% unclassified is concerning
            problematic_sources.append((source, 'Too many unclassified', unclassified_pct))
    
    print(f"\n⚠️  PROBLEMATIC SOURCES IDENTIFIED:")
    for source, issue, percentage in problematic_sources:
        print(f"  {source}: {issue} ({percentage:.1f}%)")
    
    return merged_df, problematic_sources

def analyze_training_data_gaps():
    """Analyze training data for coverage gaps."""
    
    print("\n3. ANALYZING TRAINING DATA GAPS")
    print("-" * 50)
    
    try:
        training_df = pd.read_csv('data/training/dataset/enhanced_synthetic_logs.csv')
        print(f"Loaded training data: {len(training_df)} entries")
    except Exception as e:
        print(f"Error loading training data: {e}")
        return
    
    # Analyze training data coverage
    print("\nTraining data label distribution:")
    training_labels = training_df['target_label'].value_counts()
    total_training = len(training_df)
    
    for label, count in training_labels.items():
        pct = (count / total_training) * 100
        print(f"  {label}: {count} ({pct:.1f}%)")
    
    # Check for domain-specific patterns in training data
    print("\nDomain coverage in training data:")
    sources_in_training = training_df['source'].value_counts()
    
    for source, count in sources_in_training.head(10).items():
        pct = (count / total_training) * 100
        print(f"  {source}: {count} ({pct:.1f}%)")
    
    # Analyze message patterns that might be missing
    print("\nAnalyzing message patterns in training data:")
    
    # Look for HR-related patterns
    hr_patterns = ['employee', 'payroll', 'benefits', 'training', 'onboard', 'performance', 'review']
    billing_patterns = ['payment', 'invoice', 'billing', 'subscription', 'refund', 'transaction']
    analytics_patterns = ['report', 'dashboard', 'analytics', 'data warehouse', 'pipeline', 'etl']
    
    pattern_groups = {
        'HR': hr_patterns,
        'Billing': billing_patterns, 
        'Analytics': analytics_patterns
    }
    
    for domain, patterns in pattern_groups.items():
        domain_count = 0
        for pattern in patterns:
            pattern_matches = training_df['log_message'].str.contains(pattern, case=False, na=False).sum()
            domain_count += pattern_matches
        
        print(f"  {domain} domain patterns: {domain_count} matches")
        if domain_count < 10:
            print(f"    ⚠️  {domain} domain is underrepresented in training data!")

def analyze_specific_misclassifications():
    """Analyze specific misclassification patterns."""
    
    print("\n4. ANALYZING SPECIFIC MISCLASSIFICATION PATTERNS")
    print("-" * 50)
    
    # Load test data and results
    try:
        results_df = pd.read_csv('resources/output.csv')
        
        # Test each classification through the pipeline to understand why it's wrong
        print("Testing individual messages through classification pipeline:")
        print()
        
        suspicious_cases = [
            # ModernHR cases we identified
            ("ModernHR", "Employee onboarding workflow triggered", "user_action", "security_alert"),
            ("ModernHR", "Performance review cycle initiated", "user_action", "security_alert"),
            ("ModernHR", "Benefits enrollment deadline reminder sent", "user_action", "security_alert"),
            
            # Other potentially problematic cases from the results
            ("BillingSystem", "Invoice generated for customer ABC Corp", "user_action", "security_alert"),
            ("BillingSystem", "Tax calculation error for region EU", "workflow_error", "security_alert"),
            ("BillingSystem", "Automated billing reminder sent", "system_notification", "security_alert"),
            ("AnalyticsEngine", "Data warehouse sync completed", "system_notification", "security_alert"),
            ("AnalyticsEngine", "Query optimization reduced execution time by 40%", "system_notification", "security_alert"),
            ("AnalyticsEngine", "Machine learning model training initiated", "system_notification", "security_alert"),
        ]
        
        misclassification_patterns = {}
        
        for source, message, expected, actual in suspicious_cases:
            # Test through regex first
            regex_result = classify_with_regex("test", message)
            
            print(f"Message: '{message}'")
            print(f"  Source: {source}")
            print(f"  Expected: {expected}, Actual: {actual}")
            print(f"  Regex result: {regex_result}")
            
            # Analyze why it might be misclassified
            problematic_words = []
            
            # Check for security-trigger words
            security_words = ['alert', 'threat', 'suspicious', 'unauthorized', 'breach', 'violation', 'attack', 'malicious']
            for word in security_words:
                if word.lower() in message.lower():
                    problematic_words.append(f"'{word}' (security trigger)")
            
            # Check for other pattern issues
            if 'access' in message.lower():
                problematic_words.append("'access' (could trigger security patterns)")
            if 'control' in message.lower():
                problematic_words.append("'control' (could trigger security patterns)")
            if 'audit' in message.lower():
                problematic_words.append("'audit' (could trigger security patterns)")
            
            if problematic_words:
                print(f"  Potential triggers: {', '.join(problematic_words)}")
            
            # Track patterns
            domain = source.replace('ModernHR', 'HR').replace('BillingSystem', 'Billing').replace('AnalyticsEngine', 'Analytics')
            if domain not in misclassification_patterns:
                misclassification_patterns[domain] = []
            misclassification_patterns[domain].append({
                'message': message,
                'expected': expected,
                'actual': actual,
                'triggers': problematic_words
            })
            
            print()
        
        return misclassification_patterns
        
    except Exception as e:
        print(f"Error analyzing misclassifications: {e}")
        return {}

def check_training_data_quality():
    """Check training data for quality issues."""
    
    print("\n5. CHECKING TRAINING DATA QUALITY")
    print("-" * 50)
    
    try:
        training_df = pd.read_csv('data/training/dataset/enhanced_synthetic_logs.csv')
        
        # Check for duplicate messages
        duplicates = training_df.duplicated(subset=['log_message']).sum()
        print(f"Duplicate messages in training data: {duplicates}")
        
        # Check for contradictory labels (same message, different labels)
        message_labels = training_df.groupby('log_message')['target_label'].nunique()
        contradictory = message_labels[message_labels > 1]
        print(f"Messages with contradictory labels: {len(contradictory)}")
        
        if len(contradictory) > 0:
            print("Examples of contradictory labels:")
            for message in contradictory.head(5).index:
                labels = training_df[training_df['log_message'] == message]['target_label'].unique()
                print(f"  '{message}' → {list(labels)}")
        
        # Check for very short or very long messages that might be low quality
        message_lengths = training_df['log_message'].str.len()
        very_short = (message_lengths < 10).sum()
        very_long = (message_lengths > 200).sum()
        
        print(f"Very short messages (<10 chars): {very_short}")
        print(f"Very long messages (>200 chars): {very_long}")
        
        # Check for messages that might be misclassified based on obvious patterns
        print("\nChecking for potentially misclassified training examples:")
        
        potential_issues = []
        
        # Check user_action examples for non-user activities
        user_actions = training_df[training_df['target_label'] == 'user_action']
        for _, row in user_actions.iterrows():
            message = row['log_message'].lower()
            if any(word in message for word in ['system', 'automatic', 'scheduled', 'cron']) and 'user' not in message:
                potential_issues.append((row['log_message'], 'user_action', 'Might be system_notification'))
        
        # Check security_alert examples for normal operations
        security_alerts = training_df[training_df['target_label'] == 'security_alert']
        for _, row in security_alerts.iterrows():
            message = row['log_message'].lower()
            if any(word in message for word in ['completed', 'successful', 'generated', 'initiated']) and not any(word in message for word in ['unauthorized', 'failed', 'suspicious', 'breach', 'threat']):
                potential_issues.append((row['log_message'], 'security_alert', 'Might be system_notification or user_action'))
        
        print(f"Found {len(potential_issues)} potentially misclassified training examples")
        for message, label, suggestion in potential_issues[:10]:  # Show first 10
            print(f"  '{message}' (labeled as {label}) - {suggestion}")
        
        return potential_issues
        
    except Exception as e:
        print(f"Error checking training data quality: {e}")
        return []

if __name__ == "__main__":
    # Run comprehensive analysis
    merged_df, problematic_sources = comprehensive_misclassification_analysis()
    analyze_training_data_gaps()
    misclassification_patterns = analyze_specific_misclassifications()
    training_issues = check_training_data_quality()
    
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE ANALYSIS SUMMARY")
    print("="*80)
    
    print(f"\n🚨 Issues Found:")
    print(f"  • Problematic sources: {len(problematic_sources)}")
    print(f"  • Misclassification patterns: {len(misclassification_patterns)} domains affected")
    print(f"  • Training data issues: {len(training_issues)} potential problems")
    
    print(f"\n📋 Next Steps:")
    print(f"  1. Create comprehensive training data for underrepresented domains")
    print(f"  2. Fix contradictory labels in training data")
    print(f"  3. Add domain-specific examples for HR, Billing, Analytics")
    print(f"  4. Retrain model with enhanced dataset")
    print(f"  5. Validate fixes with test cases")