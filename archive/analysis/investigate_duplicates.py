import pandas as pd
import numpy as np
from collections import Counter

def investigate_duplicate_issue():
    """Detailed investigation of the duplicate problem."""
    
    print("🔍 DETAILED DUPLICATE INVESTIGATION")
    print("=" * 60)
    
    # Load original training data
    try:
        df = pd.read_csv('data/training/dataset/enhanced_synthetic_logs.csv')
        print(f"Original dataset: {len(df)} entries")
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    print("\n📊 DUPLICATE ANALYSIS:")
    
    # 1. Check exact duplicates
    exact_dups = df.duplicated().sum()
    print(f"Exact duplicate rows: {exact_dups}")
    
    # 2. Check message duplicates
    message_dups = df.duplicated(subset=['log_message']).sum()
    print(f"Duplicate messages: {message_dups}")
    
    # 3. Check message+label duplicates
    message_label_dups = df.duplicated(subset=['log_message', 'target_label']).sum()
    print(f"Duplicate message+label pairs: {message_label_dups}")
    
    # 4. Analyze the duplication pattern
    print(f"\n📈 DUPLICATION PATTERNS:")
    message_counts = df['log_message'].value_counts()
    
    # Show distribution of duplicate counts
    dup_distribution = Counter(message_counts.values)
    print("Messages appearing X times:")
    for count, frequency in sorted(dup_distribution.items()):
        if count > 1:
            print(f"  {count} times: {frequency} unique messages ({frequency * count} total entries)")
    
    # 5. Show most duplicated messages
    print(f"\nTop 10 most duplicated messages:")
    for i, (message, count) in enumerate(message_counts.head(10).items(), 1):
        labels = df[df['log_message'] == message]['target_label'].unique()
        sources = df[df['log_message'] == message]['source'].unique()
        print(f"{i:2d}. '{message[:60]}...' → {count} times, labels: {list(labels)}, sources: {len(sources)} different")
    
    # 6. Check if duplicates are legitimate or problematic
    print(f"\n🔍 DUPLICATE LEGITIMACY CHECK:")
    
    # Check for messages with multiple labels (problematic)
    conflicting_messages = 0
    total_unique_messages = len(message_counts)
    
    for message in df['log_message'].unique():
        labels = df[df['log_message'] == message]['target_label'].unique()
        if len(labels) > 1:
            conflicting_messages += 1
            if conflicting_messages <= 5:  # Show first 5 examples
                print(f"  Conflicting: '{message[:50]}...' → {list(labels)}")
    
    print(f"Messages with conflicting labels: {conflicting_messages} out of {total_unique_messages}")
    
    # 7. Alternative deduplication strategies
    print(f"\n🛠️  DEDUPLICATION STRATEGIES:")
    
    # Strategy 1: Remove only exact duplicates
    strategy1_df = df.drop_duplicates()
    print(f"Strategy 1 - Remove exact duplicates only: {len(strategy1_df)} entries (loss: {len(df) - len(strategy1_df)})")
    
    # Strategy 2: Keep all but remove message+label duplicates
    strategy2_df = df.drop_duplicates(subset=['log_message', 'target_label'])
    print(f"Strategy 2 - Remove message+label duplicates: {len(strategy2_df)} entries (loss: {len(df) - len(strategy2_df)})")
    
    # Strategy 3: Smart deduplication - reduce high-frequency messages but keep variety
    strategy3_df = smart_deduplication(df.copy())
    print(f"Strategy 3 - Smart deduplication: {len(strategy3_df)} entries (loss: {len(df) - len(strategy3_df)})")
    
    return df, message_counts

def smart_deduplication(df):
    """Smart deduplication that preserves training data variety while reducing excessive duplicates."""
    
    print("\n🧠 APPLYING SMART DEDUPLICATION:")
    
    # Step 1: Remove exact duplicates
    df = df.drop_duplicates()
    print(f"  After removing exact duplicates: {len(df)} entries")
    
    # Step 2: For messages appearing more than 10 times, reduce to max 10 instances
    # But keep label diversity
    
    reduced_rows = []
    message_counts = df['log_message'].value_counts()
    
    for message in df['log_message'].unique():
        message_rows = df[df['log_message'] == message].copy()
        
        if len(message_rows) <= 10:
            # Keep all if 10 or fewer
            reduced_rows.extend(message_rows.to_dict('records'))
        else:
            # Keep up to 10, but ensure label diversity
            labels = message_rows['target_label'].unique()
            
            if len(labels) == 1:
                # Single label - keep random 10
                sampled = message_rows.sample(n=10, random_state=42)
                reduced_rows.extend(sampled.to_dict('records'))
            else:
                # Multiple labels - keep representation of each label
                kept_rows = []
                max_per_label = max(1, 10 // len(labels))
                
                for label in labels:
                    label_rows = message_rows[message_rows['target_label'] == label]
                    if len(label_rows) <= max_per_label:
                        kept_rows.extend(label_rows.to_dict('records'))
                    else:
                        sampled = label_rows.sample(n=max_per_label, random_state=42)
                        kept_rows.extend(sampled.to_dict('records'))
                
                # If we have space, add more randomly
                remaining_space = 10 - len(kept_rows)
                if remaining_space > 0:
                    excluded_indices = [row['index'] if 'index' in row else i for i, row in enumerate(kept_rows)]
                    remaining_rows = message_rows[~message_rows.index.isin(excluded_indices)]
                    if len(remaining_rows) > 0:
                        additional = remaining_rows.sample(n=min(remaining_space, len(remaining_rows)), random_state=42)
                        kept_rows.extend(additional.to_dict('records'))
                
                reduced_rows.extend(kept_rows)
    
    smart_df = pd.DataFrame(reduced_rows)
    print(f"  After smart deduplication: {len(smart_df)} entries")
    
    return smart_df

def create_enhanced_training_dataset():
    """Create enhanced training dataset with smart deduplication and comprehensive domain coverage."""
    
    print("\n🚀 CREATING ENHANCED TRAINING DATASET")
    print("=" * 60)
    
    # Load original data
    try:
        df = pd.read_csv('data/training/dataset/enhanced_synthetic_logs.csv')
        print(f"Original dataset: {len(df)} entries")
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
    
    # Apply smart deduplication
    cleaned_df = smart_deduplication(df.copy())
    
    # Add comprehensive domain-specific training data
    print("\n📚 Adding comprehensive domain-specific training data...")
    
    # Generate more comprehensive training examples
    new_training_data = []
    
    # HR Domain (extensive coverage)
    hr_examples = [
        # User Actions - HR Operations
        ("HRSystem", "Employee onboarding workflow initiated for new hire", "user_action"),
        ("HRSystem", "Payroll processing completed for 250 employees", "user_action"),
        ("HRSystem", "Performance review cycle started for Q3", "user_action"),
        ("HRSystem", "Leave request submitted by employee ID 12345", "user_action"),
        ("HRSystem", "Benefits enrollment completed for employee", "user_action"),
        ("HRSystem", "Training module assignment completed", "user_action"),
        ("HRSystem", "Employee profile updated successfully", "user_action"),
        ("HRSystem", "Salary adjustment processed for promotion", "user_action"),
        ("HRSystem", "Time-off request approved by manager", "user_action"),
        ("HRSystem", "Employee termination workflow initiated", "user_action"),
        ("HRSystem", "Position posting published to job board", "user_action"),
        ("HRSystem", "Interview feedback submitted", "user_action"),
        ("HRSystem", "Employee satisfaction survey completed", "user_action"),
        ("HRSystem", "Department transfer request processed", "user_action"),
        ("HRSystem", "Emergency contact information updated", "user_action"),
        
        # ModernHR specific examples
        ("ModernHR", "Employee onboarding workflow initiated", "user_action"),
        ("ModernHR", "Payroll calculation completed successfully", "user_action"),
        ("ModernHR", "Performance review cycle started", "user_action"),
        ("ModernHR", "Leave request approved for employee", "user_action"),
        ("ModernHR", "Benefits enrollment reminder sent", "user_action"),
        ("ModernHR", "Training completion recorded", "user_action"),
        ("ModernHR", "Employee profile data updated", "user_action"),
        ("ModernHR", "Salary adjustment processed", "user_action"),
        ("ModernHR", "Time tracking data synchronized", "user_action"),
        ("ModernHR", "Employee directory updated", "user_action"),
        
        # System Notifications - HR
        ("HRSystem", "Automated payroll reminder sent to employees", "system_notification"),
        ("HRSystem", "HR database backup completed successfully", "system_notification"),
        ("HRSystem", "Employee anniversary notifications generated", "system_notification"),
        ("HRSystem", "Benefits enrollment period reminder sent", "system_notification"),
        ("HRSystem", "Training schedule published for next quarter", "system_notification"),
        ("HRSystem", "Performance review deadline approaching notification", "system_notification"),
        ("ModernHR", "Daily synchronization with payroll system completed", "system_notification"),
        ("ModernHR", "Employee data backup completed", "system_notification"),
        ("ModernHR", "System maintenance window scheduled", "system_notification"),
        
        # Workflow Errors - HR
        ("HRSystem", "Payroll calculation failed for employee group", "workflow_error"),
        ("HRSystem", "Employee onboarding workflow error occurred", "workflow_error"),
        ("HRSystem", "Benefits enrollment system timeout", "workflow_error"),
        ("HRSystem", "Training module loading failed", "workflow_error"),
        ("HRSystem", "Time tracking synchronization failed", "workflow_error"),
        ("ModernHR", "Employee data synchronization error", "workflow_error"),
        ("ModernHR", "Payroll integration connection timeout", "workflow_error"),
        
        # Security Alerts - HR (legitimate security)
        ("HRSystem", "Unauthorized access attempt to employee records", "security_alert"),
        ("HRSystem", "Multiple failed login attempts detected", "security_alert"),
        ("HRSystem", "Data privacy policy violation detected", "security_alert"),
        ("ModernHR", "Suspicious access pattern detected", "security_alert"),
        ("ModernHR", "Compliance audit flag raised", "security_alert"),
    ]
    
    # Billing Domain (extensive coverage)
    billing_examples = [
        # User Actions - Billing
        ("BillingSystem", "Monthly invoice generated for customer", "user_action"),
        ("BillingSystem", "Payment processed via credit card", "user_action"),
        ("BillingSystem", "Refund initiated for transaction", "user_action"),
        ("BillingSystem", "Subscription renewal processed", "user_action"),
        ("BillingSystem", "Discount code applied to order", "user_action"),
        ("BillingSystem", "Tax calculation completed for region", "user_action"),
        ("BillingSystem", "Customer billing address updated", "user_action"),
        ("BillingSystem", "Payment method verification completed", "user_action"),
        ("BillingSystem", "Invoice dispute resolution processed", "user_action"),
        ("BillingSystem", "Automatic payment setup completed", "user_action"),
        
        # System Notifications - Billing
        ("BillingSystem", "Automated billing cycle completed successfully", "system_notification"),
        ("BillingSystem", "Payment reminder sent to customers", "system_notification"),
        ("BillingSystem", "Monthly financial report generated", "system_notification"),
        ("BillingSystem", "Tax rate update applied to system", "system_notification"),
        ("BillingSystem", "Billing database backup completed", "system_notification"),
        
        # Workflow Errors - Billing
        ("BillingSystem", "Credit card authorization failed", "workflow_error"),
        ("BillingSystem", "Payment gateway connection timeout", "workflow_error"),
        ("BillingSystem", "Invoice generation process failed", "workflow_error"),
        ("BillingSystem", "Tax calculation service unavailable", "workflow_error"),
        
        # Security Alerts - Billing
        ("BillingSystem", "Fraudulent transaction detected", "security_alert"),
        ("BillingSystem", "Unusual payment pattern identified", "security_alert"),
        ("BillingSystem", "Multiple failed payment attempts", "security_alert"),
    ]
    
    # Analytics Domain (extensive coverage)
    analytics_examples = [
        # System Notifications - Analytics
        ("AnalyticsEngine", "Daily analytics report generation started", "system_notification"),
        ("AnalyticsEngine", "Data warehouse ETL process completed", "system_notification"),
        ("AnalyticsEngine", "Real-time dashboard metrics updated", "system_notification"),
        ("AnalyticsEngine", "Machine learning model training initiated", "system_notification"),
        ("AnalyticsEngine", "Data quality validation passed", "system_notification"),
        ("AnalyticsEngine", "Automated backup process completed", "system_notification"),
        ("AnalyticsEngine", "Performance optimization routine finished", "system_notification"),
        ("AnalyticsEngine", "Data archival process completed", "system_notification"),
        ("AnalyticsEngine", "Query cache refresh completed", "system_notification"),
        ("AnalyticsEngine", "System health metrics collected", "system_notification"),
        
        # User Actions - Analytics
        ("AnalyticsEngine", "Custom report generated by user request", "user_action"),
        ("AnalyticsEngine", "Dashboard configuration updated", "user_action"),
        ("AnalyticsEngine", "Data export initiated for analysis", "user_action"),
        ("AnalyticsEngine", "Query optimization applied", "user_action"),
        ("AnalyticsEngine", "Data visualization created", "user_action"),
        
        # Workflow Errors - Analytics
        ("AnalyticsEngine", "ETL pipeline execution failed", "workflow_error"),
        ("AnalyticsEngine", "Database query timeout occurred", "workflow_error"),
        ("AnalyticsEngine", "Report generation process failed", "workflow_error"),
        ("AnalyticsEngine", "Data synchronization error", "workflow_error"),
    ]
    
    # Database System (to fix DatabaseSystem misclassifications)
    database_examples = [
        # System Notifications - Database
        ("DatabaseSystem", "Automated database backup completed", "system_notification"),
        ("DatabaseSystem", "Index optimization process finished", "system_notification"),
        ("DatabaseSystem", "Database maintenance window completed", "system_notification"),
        ("DatabaseSystem", "Query performance statistics updated", "system_notification"),
        ("DatabaseSystem", "Database connection pool optimized", "system_notification"),
        
        # User Actions - Database
        ("DatabaseSystem", "Database schema update applied", "user_action"),
        ("DatabaseSystem", "Data migration process initiated", "user_action"),
        ("DatabaseSystem", "Database user permissions updated", "user_action"),
        
        # Workflow Errors - Database
        ("DatabaseSystem", "Database connection timeout", "workflow_error"),
        ("DatabaseSystem", "Query execution failed", "workflow_error"),
        ("DatabaseSystem", "Backup process interrupted", "workflow_error"),
        
        # Security Alerts - Database
        ("DatabaseSystem", "Unauthorized database access attempt", "security_alert"),
        ("DatabaseSystem", "SQL injection attack detected", "security_alert"),
    ]
    
    # File System (to fix FileSystem misclassifications)
    filesystem_examples = [
        # System Notifications - FileSystem
        ("FileSystem", "File system cleanup completed", "system_notification"),
        ("FileSystem", "Disk space optimization finished", "system_notification"),
        ("FileSystem", "File backup process completed", "system_notification"),
        ("FileSystem", "Archive compression completed", "system_notification"),
        
        # User Actions - FileSystem
        ("FileSystem", "File upload completed successfully", "user_action"),
        ("FileSystem", "Document sharing permissions updated", "user_action"),
        ("FileSystem", "File synchronization initiated", "user_action"),
        
        # Workflow Errors - FileSystem
        ("FileSystem", "File upload process failed", "workflow_error"),
        ("FileSystem", "Disk space insufficient error", "workflow_error"),
        
        # Security Alerts - FileSystem
        ("FileSystem", "Unauthorized file access detected", "security_alert"),
    ]
    
    # Monitoring System (to fix MonitoringSystem misclassifications)
    monitoring_examples = [
        # System Notifications - Monitoring
        ("MonitoringSystem", "System health check completed", "system_notification"),
        ("MonitoringSystem", "Performance metrics collected", "system_notification"),
        ("MonitoringSystem", "Alert threshold configuration updated", "system_notification"),
        ("MonitoringSystem", "Monitoring data archived", "system_notification"),
        
        # Security Alerts - Monitoring (legitimate security)
        ("MonitoringSystem", "CPU usage threshold exceeded", "security_alert"),
        ("MonitoringSystem", "Memory consumption critical alert", "security_alert"),
        ("MonitoringSystem", "Unusual network traffic detected", "security_alert"),
        ("MonitoringSystem", "System resource anomaly detected", "security_alert"),
        
        # Workflow Errors - Monitoring
        ("MonitoringSystem", "Metric collection failed", "workflow_error"),
        ("MonitoringSystem", "Alert delivery failure", "workflow_error"),
    ]
    
    # Combine all new training data
    all_new_examples = (hr_examples + billing_examples + analytics_examples + 
                       database_examples + filesystem_examples + monitoring_examples)
    
    # Convert to DataFrame
    current_time = "2025-09-14 12:00:00"
    new_rows = []
    for source, message, label in all_new_examples:
        new_rows.append({
            'timestamp': current_time,
            'source': source,
            'log_message': message,
            'target_label': label,
            'complexity': 'bert'
        })
    
    new_df = pd.DataFrame(new_rows)
    
    # Combine with cleaned original data
    enhanced_df = pd.concat([cleaned_df, new_df], ignore_index=True)
    
    # Final deduplication (only exact duplicates)
    enhanced_df = enhanced_df.drop_duplicates(subset=['log_message', 'target_label'])
    
    print(f"Added {len(new_df)} new training examples")
    print(f"Final enhanced dataset: {len(enhanced_df)} entries")
    
    # Show final distribution
    print("\nFinal label distribution:")
    final_distribution = enhanced_df['target_label'].value_counts()
    for label, count in final_distribution.items():
        pct = (count / len(enhanced_df)) * 100
        print(f"  {label}: {count} ({pct:.1f}%)")
    
    # Save the enhanced dataset
    output_path = 'data/training/dataset/enhanced_comprehensive_dataset.csv'
    enhanced_df.to_csv(output_path, index=False)
    print(f"\nSaved enhanced dataset to: {output_path}")
    
    return enhanced_df, output_path

if __name__ == "__main__":
    # First investigate the duplicate issue
    df, message_counts = investigate_duplicate_issue()
    
    # Then create enhanced dataset
    enhanced_df, output_path = create_enhanced_training_dataset()
    
    if enhanced_df is not None:
        print(f"\n✅ ENHANCED TRAINING DATASET READY")
        print(f"   File: {output_path}")
        print(f"   Entries: {len(enhanced_df)} (vs original 2,500)")
        print(f"   Smart deduplication: ✅")
        print(f"   Comprehensive domain coverage: ✅")
        print(f"   Ready for model retraining: ✅")