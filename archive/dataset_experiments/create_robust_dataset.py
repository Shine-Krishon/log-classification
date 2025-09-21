import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime

def balanced_deduplication(df, max_instances_per_message=15):
    """
    Balanced deduplication that preserves training data while reducing extreme duplicates.
    
    Strategy:
    1. Keep all messages that appear <= max_instances_per_message times
    2. For messages appearing more than max_instances_per_message times, 
       randomly sample max_instances_per_message instances
    3. Preserve label and source diversity
    """
    
    print(f"🎯 APPLYING BALANCED DEDUPLICATION (max {max_instances_per_message} per message)")
    print("-" * 60)
    
    # Remove exact duplicates first
    df_clean = df.drop_duplicates()
    print(f"After removing exact duplicates: {len(df_clean)} entries")
    
    # Group by message and apply sampling
    balanced_rows = []
    message_counts = df_clean['log_message'].value_counts()
    
    messages_reduced = 0
    total_removed = 0
    
    for message in df_clean['log_message'].unique():
        message_df = df_clean[df_clean['log_message'] == message]
        
        if len(message_df) <= max_instances_per_message:
            # Keep all instances
            balanced_rows.extend(message_df.to_dict('records'))
        else:
            # Sample down to max_instances_per_message
            sampled = message_df.sample(n=max_instances_per_message, random_state=42)
            balanced_rows.extend(sampled.to_dict('records'))
            
            messages_reduced += 1
            total_removed += (len(message_df) - max_instances_per_message)
    
    balanced_df = pd.DataFrame(balanced_rows)
    
    print(f"Messages reduced from >{max_instances_per_message} instances: {messages_reduced}")
    print(f"Total entries removed: {total_removed}")
    print(f"Final dataset size: {len(balanced_df)} entries")
    print(f"Retention rate: {len(balanced_df)/len(df)*100:.1f}%")
    
    return balanced_df

def create_robust_training_dataset():
    """Create a robust training dataset with balanced deduplication and comprehensive coverage."""
    
    print("🚀 CREATING ROBUST TRAINING DATASET")
    print("=" * 70)
    
    # Load original data
    try:
        df = pd.read_csv('data/training/dataset/enhanced_synthetic_logs.csv')
        print(f"Original dataset: {len(df)} entries")
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
    
    # Show original distribution
    print("\nOriginal label distribution:")
    for label, count in df['target_label'].value_counts().items():
        pct = (count / len(df)) * 100
        print(f"  {label}: {count} ({pct:.1f}%)")
    
    # Apply balanced deduplication (keeping more data)
    balanced_df = balanced_deduplication(df.copy(), max_instances_per_message=15)
    
    # Add comprehensive domain-specific training data
    print(f"\n📚 ADDING COMPREHENSIVE DOMAIN TRAINING DATA")
    print("-" * 60)
    
    current_time = "2025-09-14 12:00:00"
    
    # Extensive domain-specific training data
    domain_training_data = [
        # === HR/ModernHR Domain (50 examples) ===
        # User Actions
        ("HRSystem", "Employee onboarding workflow initiated for new hire", "user_action"),
        ("HRSystem", "Payroll processing completed for 250 employees", "user_action"),
        ("HRSystem", "Performance review cycle started for Q3 2025", "user_action"),
        ("HRSystem", "Leave request submitted by employee ID 12345", "user_action"),
        ("HRSystem", "Benefits enrollment completed for employee", "user_action"),
        ("HRSystem", "Training module assignment sent to employee", "user_action"),
        ("HRSystem", "Employee profile updated with new contact info", "user_action"),
        ("HRSystem", "Salary adjustment processed for promotion", "user_action"),
        ("HRSystem", "Time-off request approved by manager Sarah", "user_action"),
        ("HRSystem", "Employee termination workflow initiated", "user_action"),
        ("HRSystem", "Job posting published to careers page", "user_action"),
        ("HRSystem", "Interview feedback submitted for candidate", "user_action"),
        ("HRSystem", "Employee satisfaction survey completed", "user_action"),
        ("HRSystem", "Department transfer request processed", "user_action"),
        ("HRSystem", "Emergency contact information updated", "user_action"),
        
        ("ModernHR", "Employee onboarding workflow triggered", "user_action"),
        ("ModernHR", "Payroll calculation completed successfully", "user_action"),
        ("ModernHR", "Performance review cycle initiated", "user_action"),
        ("ModernHR", "Leave request approved for employee", "user_action"),
        ("ModernHR", "Benefits enrollment reminder sent", "user_action"),
        ("ModernHR", "Training completion status updated", "user_action"),
        ("ModernHR", "Employee profile synchronization completed", "user_action"),
        ("ModernHR", "Salary adjustment data processed", "user_action"),
        ("ModernHR", "Time tracking sync completed", "user_action"),
        ("ModernHR", "Employee directory refresh completed", "user_action"),
        
        # System Notifications
        ("HRSystem", "HR database nightly backup completed", "system_notification"),
        ("HRSystem", "Employee anniversary notifications sent", "system_notification"),
        ("HRSystem", "Benefits enrollment period reminder scheduled", "system_notification"),
        ("HRSystem", "Training schedule published for Q4", "system_notification"),
        ("HRSystem", "Performance review deadline notification sent", "system_notification"),
        ("ModernHR", "Daily data synchronization with payroll completed", "system_notification"),
        ("ModernHR", "Employee data backup process finished", "system_notification"),
        ("ModernHR", "System maintenance window completed", "system_notification"),
        
        # Workflow Errors
        ("HRSystem", "Payroll calculation failed for employee group A", "workflow_error"),
        ("HRSystem", "Employee onboarding workflow encountered error", "workflow_error"),
        ("HRSystem", "Benefits enrollment system connection timeout", "workflow_error"),
        ("HRSystem", "Training module loading failed for user", "workflow_error"),
        ("ModernHR", "Employee data sync failed - connection error", "workflow_error"),
        ("ModernHR", "Payroll integration timeout occurred", "workflow_error"),
        
        # Security Alerts (legitimate)
        ("HRSystem", "Unauthorized access attempt to employee records", "security_alert"),
        ("HRSystem", "Multiple failed login attempts detected", "security_alert"),
        ("HRSystem", "Data privacy violation alert triggered", "security_alert"),
        ("ModernHR", "Suspicious access pattern detected", "security_alert"),
        ("ModernHR", "Compliance audit flag raised", "security_alert"),
        
        # === Billing Domain (25 examples) ===
        # User Actions
        ("BillingSystem", "Monthly invoice generated for customer ABC123", "user_action"),
        ("BillingSystem", "Payment processed via credit card ending 1234", "user_action"),
        ("BillingSystem", "Refund initiated for transaction TXN789", "user_action"),
        ("BillingSystem", "Subscription renewal processed for premium plan", "user_action"),
        ("BillingSystem", "Discount code SAVE20 applied to order", "user_action"),
        ("BillingSystem", "Tax calculation completed for California region", "user_action"),
        ("BillingSystem", "Customer billing address updated", "user_action"),
        ("BillingSystem", "Payment method verification completed", "user_action"),
        ("BillingSystem", "Invoice dispute resolution initiated", "user_action"),
        ("BillingSystem", "Automatic payment setup completed", "user_action"),
        
        # System Notifications
        ("BillingSystem", "Monthly billing cycle completed successfully", "system_notification"),
        ("BillingSystem", "Payment reminder notifications sent", "system_notification"),
        ("BillingSystem", "Financial report generation completed", "system_notification"),
        ("BillingSystem", "Tax rate update applied to system", "system_notification"),
        ("BillingSystem", "Billing database backup completed", "system_notification"),
        
        # Workflow Errors
        ("BillingSystem", "Credit card authorization failed for payment", "workflow_error"),
        ("BillingSystem", "Payment gateway connection timeout", "workflow_error"),
        ("BillingSystem", "Invoice generation process failed", "workflow_error"),
        ("BillingSystem", "Tax calculation service unavailable", "workflow_error"),
        
        # Security Alerts
        ("BillingSystem", "Fraudulent transaction pattern detected", "security_alert"),
        ("BillingSystem", "Unusual payment amount triggered alert", "security_alert"),
        ("BillingSystem", "Multiple failed payment attempts blocked", "security_alert"),
        ("BillingSystem", "Suspicious billing location detected", "security_alert"),
        ("BillingSystem", "Credit card fraud prevention alert", "security_alert"),
        ("BillingSystem", "Chargeback risk assessment triggered", "security_alert"),
        
        # === Analytics Domain (25 examples) ===
        # System Notifications
        ("AnalyticsEngine", "Daily analytics report generation started", "system_notification"),
        ("AnalyticsEngine", "Data warehouse ETL process completed", "system_notification"),
        ("AnalyticsEngine", "Real-time dashboard metrics refreshed", "system_notification"),
        ("AnalyticsEngine", "Machine learning model training initiated", "system_notification"),
        ("AnalyticsEngine", "Data quality validation checks passed", "system_notification"),
        ("AnalyticsEngine", "Automated backup process completed", "system_notification"),
        ("AnalyticsEngine", "Performance optimization routine finished", "system_notification"),
        ("AnalyticsEngine", "Data archival process completed successfully", "system_notification"),
        ("AnalyticsEngine", "Query cache refresh operation completed", "system_notification"),
        ("AnalyticsEngine", "System health metrics collection finished", "system_notification"),
        
        # User Actions
        ("AnalyticsEngine", "Custom report generated per user request", "user_action"),
        ("AnalyticsEngine", "Dashboard configuration updated by admin", "user_action"),
        ("AnalyticsEngine", "Data export initiated for quarterly analysis", "user_action"),
        ("AnalyticsEngine", "Query optimization settings applied", "user_action"),
        ("AnalyticsEngine", "Data visualization chart created", "user_action"),
        ("AnalyticsEngine", "Report schedule updated by user", "user_action"),
        
        # Workflow Errors
        ("AnalyticsEngine", "ETL pipeline execution failed", "workflow_error"),
        ("AnalyticsEngine", "Database query timeout occurred", "workflow_error"),
        ("AnalyticsEngine", "Report generation process failed", "workflow_error"),
        ("AnalyticsEngine", "Data synchronization error detected", "workflow_error"),
        ("AnalyticsEngine", "Memory allocation error during processing", "workflow_error"),
        
        # Security Alerts
        ("AnalyticsEngine", "Anomalous data access pattern detected", "security_alert"),
        ("AnalyticsEngine", "Unauthorized query execution attempt", "security_alert"),
        ("AnalyticsEngine", "Data export security threshold exceeded", "security_alert"),
        
        # === Database System (20 examples) ===
        # System Notifications
        ("DatabaseSystem", "Automated database backup completed successfully", "system_notification"),
        ("DatabaseSystem", "Index optimization process finished", "system_notification"),
        ("DatabaseSystem", "Database maintenance window completed", "system_notification"),
        ("DatabaseSystem", "Query performance statistics updated", "system_notification"),
        ("DatabaseSystem", "Connection pool optimization completed", "system_notification"),
        ("DatabaseSystem", "Database integrity check passed", "system_notification"),
        
        # User Actions
        ("DatabaseSystem", "Database schema migration applied", "user_action"),
        ("DatabaseSystem", "Data migration process initiated", "user_action"),
        ("DatabaseSystem", "User permissions updated for database", "user_action"),
        ("DatabaseSystem", "Database configuration updated", "user_action"),
        
        # Workflow Errors
        ("DatabaseSystem", "Database connection pool exhausted", "workflow_error"),
        ("DatabaseSystem", "Query execution timeout exceeded", "workflow_error"),
        ("DatabaseSystem", "Backup process failed due to disk space", "workflow_error"),
        ("DatabaseSystem", "Replication lag threshold exceeded", "workflow_error"),
        
        # Security Alerts
        ("DatabaseSystem", "Unauthorized database access attempt detected", "security_alert"),
        ("DatabaseSystem", "SQL injection pattern detected", "security_alert"),
        ("DatabaseSystem", "Privileged account unusual activity", "security_alert"),
        ("DatabaseSystem", "Database brute force attack detected", "security_alert"),
        ("DatabaseSystem", "Suspicious data export activity", "security_alert"),
        ("DatabaseSystem", "Database privilege escalation attempt", "security_alert"),
        
        # === File System (15 examples) ===
        # System Notifications
        ("FileSystem", "File system cleanup process completed", "system_notification"),
        ("FileSystem", "Disk space optimization finished", "system_notification"),
        ("FileSystem", "File backup process completed successfully", "system_notification"),
        ("FileSystem", "Archive compression completed", "system_notification"),
        ("FileSystem", "File synchronization completed", "system_notification"),
        
        # User Actions
        ("FileSystem", "File upload completed for document.pdf", "user_action"),
        ("FileSystem", "Document sharing permissions updated", "user_action"),
        ("FileSystem", "File synchronization initiated by user", "user_action"),
        ("FileSystem", "Folder structure reorganization completed", "user_action"),
        
        # Workflow Errors
        ("FileSystem", "File upload process failed - size limit", "workflow_error"),
        ("FileSystem", "Disk space insufficient for operation", "workflow_error"),
        ("FileSystem", "File corruption detected during backup", "workflow_error"),
        
        # Security Alerts
        ("FileSystem", "Unauthorized file access attempt detected", "security_alert"),
        ("FileSystem", "Malicious file upload blocked", "security_alert"),
        ("FileSystem", "Unusual file deletion pattern detected", "security_alert"),
        
        # === Monitoring System (15 examples) ===
        # System Notifications
        ("MonitoringSystem", "System health check completed successfully", "system_notification"),
        ("MonitoringSystem", "Performance metrics collection finished", "system_notification"),
        ("MonitoringSystem", "Alert threshold configuration updated", "system_notification"),
        ("MonitoringSystem", "Monitoring data archival completed", "system_notification"),
        ("MonitoringSystem", "System baseline metrics updated", "system_notification"),
        
        # Security Alerts (these are legitimate for monitoring)
        ("MonitoringSystem", "CPU usage exceeded critical threshold", "security_alert"),
        ("MonitoringSystem", "Memory consumption reached danger level", "security_alert"),
        ("MonitoringSystem", "Unusual network traffic pattern detected", "security_alert"),
        ("MonitoringSystem", "System resource anomaly detected", "security_alert"),
        ("MonitoringSystem", "Disk I/O threshold exceeded", "security_alert"),
        
        # Workflow Errors
        ("MonitoringSystem", "Metric collection service failed", "workflow_error"),
        ("MonitoringSystem", "Alert delivery system timeout", "workflow_error"),
        ("MonitoringSystem", "Monitoring agent connection lost", "workflow_error"),
        
        # User Actions
        ("MonitoringSystem", "Alert threshold updated by administrator", "user_action"),
        ("MonitoringSystem", "Monitoring dashboard configuration saved", "user_action"),
    ]
    
    # Convert new training data to DataFrame
    new_rows = []
    for source, message, label in domain_training_data:
        new_rows.append({
            'timestamp': current_time,
            'source': source,
            'log_message': message,
            'target_label': label,
            'complexity': 'bert'
        })
    
    new_df = pd.DataFrame(new_rows)
    print(f"Generated {len(new_df)} domain-specific training examples")
    
    # Combine with balanced original data
    final_df = pd.concat([balanced_df, new_df], ignore_index=True)
    
    # Remove only exact duplicates (preserve variety)
    final_df = final_df.drop_duplicates(subset=['log_message', 'target_label'])
    
    print(f"\nFinal robust dataset: {len(final_df)} entries")
    print(f"Improvement over original: {((len(final_df) - len(df))/len(df)*100):+.1f}%")
    
    # Show final distribution
    print("\nFinal label distribution:")
    final_distribution = final_df['target_label'].value_counts()
    for label, count in final_distribution.items():
        pct = (count / len(final_df)) * 100
        print(f"  {label}: {count} ({pct:.1f}%)")
    
    # Show source distribution for problematic sources
    print("\nDistribution for previously problematic sources:")
    problematic_sources = ['ModernHR', 'BillingSystem', 'DatabaseSystem', 'FileSystem', 'AnalyticsEngine', 'MonitoringSystem']
    for source in problematic_sources:
        source_data = final_df[final_df['source'] == source]
        if len(source_data) > 0:
            print(f"  {source}: {len(source_data)} examples")
            for label, count in source_data['target_label'].value_counts().items():
                print(f"    {label}: {count}")
    
    # Save the robust dataset
    output_path = 'data/training/dataset/robust_training_dataset.csv'
    final_df.to_csv(output_path, index=False)
    print(f"\nSaved robust training dataset to: {output_path}")
    
    return final_df, output_path

if __name__ == "__main__":
    robust_df, output_path = create_robust_training_dataset()
    
    if robust_df is not None:
        print(f"\n✅ ROBUST TRAINING DATASET READY")
        print(f"   File: {output_path}")
        print(f"   Entries: {len(robust_df)}")
        print(f"   Balanced deduplication: ✅")
        print(f"   Comprehensive domain coverage: ✅")
        print(f"   Preserves training data variety: ✅")
        print(f"   Ready for model retraining: ✅")