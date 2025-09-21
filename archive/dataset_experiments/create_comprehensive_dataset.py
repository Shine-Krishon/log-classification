import pandas as pd
import numpy as np
from datetime import datetime

def analyze_duplicate_issue():
    """Analyze and fix the duplicate issue in training data."""
    
    print("🔍 ANALYZING DUPLICATE ISSUE IN TRAINING DATA")
    print("=" * 60)
    
    # Load training data
    try:
        training_df = pd.read_csv('data/training/dataset/enhanced_synthetic_logs.csv')
        print(f"Loaded training data: {len(training_df)} entries")
    except Exception as e:
        print(f"Error loading training data: {e}")
        return None
    
    # Analyze duplicates in detail
    print("\nAnalyzing duplicates:")
    total_records = len(training_df)
    
    # Check for exact duplicate rows
    exact_duplicates = training_df.duplicated().sum()
    print(f"  Exact duplicate rows: {exact_duplicates}")
    
    # Check for duplicate messages (same message, potentially different labels)
    message_duplicates = training_df.duplicated(subset=['log_message']).sum()
    print(f"  Duplicate messages: {message_duplicates}")
    
    # Check for duplicate message+label combinations
    message_label_duplicates = training_df.duplicated(subset=['log_message', 'target_label']).sum()
    print(f"  Duplicate message+label: {message_label_duplicates}")
    
    # Find the most duplicated messages
    message_counts = training_df['log_message'].value_counts()
    highly_duplicated = message_counts[message_counts > 5]
    
    print(f"\nMessages appearing more than 5 times: {len(highly_duplicated)}")
    if len(highly_duplicated) > 0:
        print("Examples:")
        for message, count in highly_duplicated.head(10).items():
            labels = training_df[training_df['log_message'] == message]['target_label'].unique()
            print(f"  '{message}' (appears {count} times) → labels: {list(labels)}")
    
    # Remove exact duplicates first
    print(f"\nCleaning training data...")
    cleaned_df = training_df.drop_duplicates()
    print(f"  After removing exact duplicates: {len(cleaned_df)} entries ({len(training_df) - len(cleaned_df)} removed)")
    
    # For remaining message duplicates, keep only one instance per message-label combination
    final_df = cleaned_df.drop_duplicates(subset=['log_message', 'target_label'])
    print(f"  After removing message+label duplicates: {len(final_df)} entries ({len(cleaned_df) - len(final_df)} removed)")
    
    # Check for remaining issues
    remaining_message_duplicates = final_df['log_message'].value_counts()
    conflicting_messages = remaining_message_duplicates[remaining_message_duplicates > 1]
    
    if len(conflicting_messages) > 0:
        print(f"\n⚠️  Found {len(conflicting_messages)} messages with multiple labels:")
        for message in conflicting_messages.head(5).index:
            labels = final_df[final_df['log_message'] == message]['target_label'].unique()
            print(f"  '{message}' → {list(labels)}")
    
    return final_df, conflicting_messages

def create_comprehensive_training_dataset():
    """Create a comprehensive training dataset addressing all identified issues."""
    
    print("\n🔧 CREATING COMPREHENSIVE TRAINING DATASET")
    print("=" * 60)
    
    # Get cleaned base data
    cleaned_df, conflicting_messages = analyze_duplicate_issue()
    
    if cleaned_df is None:
        return None
    
    # Resolve conflicting messages by keeping the most appropriate label
    print("\nResolving conflicting message labels...")
    
    # Manual resolution for common conflicts
    label_priority = {
        'security_alert': 5,  # Highest priority - security is critical
        'workflow_error': 4,  # High priority - errors are important
        'user_action': 3,     # Medium priority - user activities
        'deprecation_warning': 2,  # Lower priority - warnings
        'system_notification': 1,  # Lowest priority - general notifications
        'unclassified': 0     # Last resort
    }
    
    resolved_df = cleaned_df.copy()
    
    for message in conflicting_messages.index:
        message_entries = resolved_df[resolved_df['log_message'] == message]
        
        # Choose the label with highest priority
        best_label = max(message_entries['target_label'], key=lambda x: label_priority.get(x, 0))
        
        # Keep only the entry with the best label
        resolved_df = resolved_df[~((resolved_df['log_message'] == message) & (resolved_df['target_label'] != best_label))]
    
    print(f"Resolved conflicts, final base dataset: {len(resolved_df)} entries")
    
    # Add comprehensive domain-specific training data
    print("\nAdding domain-specific training data...")
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # HR Domain Training Data (ModernHR issues)
    hr_data = [
        # User Actions - HR Operations
        ("HRSystem", "Employee onboarding workflow triggered", "user_action"),
        ("HRSystem", "Employee onboarding process completed", "user_action"),
        ("HRSystem", "Payroll calculation completed for 250 employees", "user_action"),
        ("HRSystem", "Payroll processing initiated", "user_action"),
        ("HRSystem", "Performance review cycle initiated", "user_action"),
        ("HRSystem", "Performance evaluation submitted", "user_action"),
        ("HRSystem", "Leave request approved for EMP001", "user_action"),
        ("HRSystem", "Vacation request submitted", "user_action"),
        ("HRSystem", "Benefits enrollment deadline reminder sent", "user_action"),
        ("HRSystem", "Benefits claim processed", "user_action"),
        ("HRSystem", "Training module completion recorded", "user_action"),
        ("HRSystem", "Training certificate generated", "user_action"),
        ("HRSystem", "Employee profile updated", "user_action"),
        ("HRSystem", "New hire documentation completed", "user_action"),
        ("HRSystem", "Employee promotion recorded", "user_action"),
        ("HRSystem", "Salary adjustment processed", "user_action"),
        ("ModernHR", "Employee onboarding workflow triggered", "user_action"),
        ("ModernHR", "Payroll calculation completed for employees", "user_action"),
        ("ModernHR", "Performance review cycle initiated", "user_action"),
        ("ModernHR", "Leave request approved", "user_action"),
        ("ModernHR", "Benefits enrollment reminder sent", "user_action"),
        ("ModernHR", "Training module completion recorded", "user_action"),
        
        # System Notifications - HR System Events
        ("HRSystem", "Time tracking synchronization completed", "system_notification"),
        ("HRSystem", "Employee directory updated", "system_notification"),
        ("HRSystem", "HR database backup completed", "system_notification"),
        ("HRSystem", "Payroll system maintenance completed", "system_notification"),
        ("HRSystem", "Benefits enrollment period started", "system_notification"),
        ("HRSystem", "Training schedule published", "system_notification"),
        ("ModernHR", "Time tracking synchronization completed", "system_notification"),
        ("ModernHR", "Employee directory updated", "system_notification"),
        
        # Security Alerts - Legitimate HR Security
        ("HRSystem", "Compliance audit report generated", "security_alert"),
        ("HRSystem", "Access control review scheduled", "security_alert"),
        ("HRSystem", "Unauthorized access to employee records", "security_alert"),
        ("HRSystem", "Data privacy violation detected", "security_alert"),
        ("ModernHR", "Compliance audit report generated", "security_alert"),
        ("ModernHR", "Access control review scheduled", "security_alert"),
        
        # Workflow Errors - HR System Failures
        ("HRSystem", "Payroll calculation failed", "workflow_error"),
        ("HRSystem", "Employee onboarding workflow error", "workflow_error"),
        ("HRSystem", "Benefits enrollment system timeout", "workflow_error"),
        ("HRSystem", "Training module loading failed", "workflow_error"),
    ]
    
    # Billing Domain Training Data (BillingSystem issues)
    billing_data = [
        # User Actions - Billing Operations
        ("BillingSystem", "Invoice generated for customer", "user_action"),
        ("BillingSystem", "Payment processed successfully", "user_action"),
        ("BillingSystem", "Refund initiated for transaction", "user_action"),
        ("BillingSystem", "Subscription renewal processed", "user_action"),
        ("BillingSystem", "Discount code applied successfully", "user_action"),
        
        # System Notifications - Billing System Events
        ("BillingSystem", "Automated billing reminder sent", "system_notification"),
        ("BillingSystem", "Monthly billing cycle completed", "system_notification"),
        ("BillingSystem", "Billing database backup completed", "system_notification"),
        ("BillingSystem", "Invoice batch processing completed", "system_notification"),
        
        # Workflow Errors - Billing Failures
        ("BillingSystem", "Credit card authorization failed", "workflow_error"),
        ("BillingSystem", "Payment gateway timeout occurred", "workflow_error"),
        ("BillingSystem", "Tax calculation error for region", "workflow_error"),
        ("BillingSystem", "Invoice generation failed", "workflow_error"),
        
        # Security Alerts - Billing Security
        ("BillingSystem", "Fraud detection alert triggered", "security_alert"),
        ("BillingSystem", "Unusual payment pattern detected", "security_alert"),
        ("BillingSystem", "Suspicious transaction blocked", "security_alert"),
    ]
    
    # Analytics Domain Training Data (AnalyticsEngine issues)
    analytics_data = [
        # System Notifications - Analytics Operations
        ("AnalyticsEngine", "Daily report generation started", "system_notification"),
        ("AnalyticsEngine", "Data warehouse sync completed", "system_notification"),
        ("AnalyticsEngine", "ETL pipeline executed successfully", "system_notification"),
        ("AnalyticsEngine", "Query optimization completed", "system_notification"),
        ("AnalyticsEngine", "Machine learning model training initiated", "system_notification"),
        ("AnalyticsEngine", "Real-time dashboard updated", "system_notification"),
        ("AnalyticsEngine", "Data quality check passed", "system_notification"),
        ("AnalyticsEngine", "Backup verification successful", "system_notification"),
        ("AnalyticsEngine", "Archive process completed", "system_notification"),
        ("AnalyticsEngine", "Performance metrics calculation finished", "system_notification"),
        
        # Workflow Errors - Analytics Failures
        ("AnalyticsEngine", "Data pipeline execution failed", "workflow_error"),
        ("AnalyticsEngine", "Report generation failed", "workflow_error"),
        ("AnalyticsEngine", "Database query timeout", "workflow_error"),
        ("AnalyticsEngine", "ETL process error", "workflow_error"),
        
        # User Actions - Analytics User Operations
        ("AnalyticsEngine", "Custom report requested by user", "user_action"),
        ("AnalyticsEngine", "Dashboard configuration updated", "user_action"),
        ("AnalyticsEngine", "Data export initiated by user", "user_action"),
    ]
    
    # Security System Training Data (to reduce false positives)
    security_data = [
        # Legitimate Security Alerts
        ("SecuritySystem", "Intrusion detection alert triggered", "security_alert"),
        ("SecuritySystem", "Unauthorized login attempt detected", "security_alert"),
        ("SecuritySystem", "Malware scan found threats", "security_alert"),
        ("SecuritySystem", "Firewall rule violation detected", "security_alert"),
        ("SecuritySystem", "Data breach attempt blocked", "security_alert"),
        
        # System Notifications - Security Operations
        ("SecuritySystem", "Security scan completed successfully", "system_notification"),
        ("SecuritySystem", "Firewall rules updated", "system_notification"),
        ("SecuritySystem", "Antivirus definitions updated", "system_notification"),
        ("SecuritySystem", "Security backup completed", "system_notification"),
    ]
    
    # Combine all new training data
    all_new_data = hr_data + billing_data + analytics_data + security_data
    
    new_training_rows = []
    for source, message, label in all_new_data:
        new_training_rows.append({
            'timestamp': current_time,
            'source': source,
            'log_message': message,
            'target_label': label,
            'complexity': 'bert'
        })
    
    new_df = pd.DataFrame(new_training_rows)
    
    # Combine with resolved base data
    final_training_df = pd.concat([resolved_df, new_df], ignore_index=True)
    
    # Final deduplication
    final_training_df = final_training_df.drop_duplicates(subset=['log_message', 'target_label'])
    
    print(f"Added {len(new_df)} new training examples")
    print(f"Final training dataset: {len(final_training_df)} entries")
    
    # Show final distribution
    print("\nFinal label distribution:")
    final_distribution = final_training_df['target_label'].value_counts()
    for label, count in final_distribution.items():
        pct = (count / len(final_training_df)) * 100
        print(f"  {label}: {count} ({pct:.1f}%)")
    
    # Save the comprehensive dataset
    output_path = 'data/training/dataset/comprehensive_training_dataset.csv'
    final_training_df.to_csv(output_path, index=False)
    print(f"\nSaved comprehensive training dataset to: {output_path}")
    
    return final_training_df, output_path

if __name__ == "__main__":
    comprehensive_df, output_path = create_comprehensive_training_dataset()
    
    if comprehensive_df is not None:
        print(f"\n✅ COMPREHENSIVE TRAINING DATASET READY")
        print(f"   File: {output_path}")
        print(f"   Entries: {len(comprehensive_df)}")
        print(f"   Duplicates removed: ✅")
        print(f"   Domain coverage enhanced: ✅")
        print(f"   Ready for model retraining: ✅")
    else:
        print(f"\n❌ Failed to create comprehensive dataset")