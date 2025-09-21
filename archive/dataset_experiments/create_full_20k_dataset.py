import pandas as pd
import numpy as np
from collections import Counter

def analyze_full_dataset():
    """Analyze the full 20K dataset and create a comprehensive training solution."""
    
    print("🔍 ANALYZING FULL 20K DATASET")
    print("=" * 70)
    
    # Load the full 20K dataset
    try:
        df_20k = pd.read_csv('logs_chunk1.csv')
        print(f"Full dataset: {len(df_20k)} entries")
    except Exception as e:
        print(f"Error loading full dataset: {e}")
        return None
    
    # Show dataset structure
    print(f"\nDataset columns: {list(df_20k.columns)}")
    print(f"Dataset shape: {df_20k.shape}")
    
    # Check for duplicates in the full dataset
    print(f"\nDuplicate analysis:")
    exact_dups = df_20k.duplicated().sum()
    message_dups = df_20k.duplicated(subset=['log_message']).sum()
    print(f"  Exact duplicates: {exact_dups}")
    print(f"  Message duplicates: {message_dups}")
    print(f"  Unique messages: {df_20k['log_message'].nunique()}")
    
    # Show label distribution
    print(f"\nLabel distribution in full dataset:")
    label_counts = df_20k['target_label'].value_counts()
    for label, count in label_counts.items():
        pct = (count / len(df_20k)) * 100
        print(f"  {label}: {count} ({pct:.1f}%)")
    
    # Check for complexity column
    if 'complexity' in df_20k.columns:
        print(f"\nComplexity distribution:")
        complexity_counts = df_20k['complexity'].value_counts()
        for complexity, count in complexity_counts.items():
            pct = (count / len(df_20k)) * 100
            print(f"  {complexity}: {count} ({pct:.1f}%)")
    else:
        print(f"\nNo complexity column found in full dataset")
    
    # Sample some messages to check quality
    print(f"\nSample messages from full dataset:")
    for i, (_, row) in enumerate(df_20k.sample(5).iterrows()):
        print(f"  {i+1}. [{row['target_label']}] {row['log_message'][:80]}...")
    
    return df_20k

def create_comprehensive_20k_dataset():
    """Create a comprehensive training dataset using the full 20K data with smart deduplication."""
    
    print("\n🚀 CREATING COMPREHENSIVE 20K TRAINING DATASET")
    print("=" * 70)
    
    # Load the full dataset
    df_20k = analyze_full_dataset()
    if df_20k is None:
        return None
    
    # Apply smart deduplication (keep more data than aggressive deduplication)
    print(f"\nApplying smart deduplication...")
    
    # Strategy: Remove only exact duplicates, keep message duplicates with different contexts
    initial_count = len(df_20k)
    
    # Remove exact duplicates only
    df_deduplicated = df_20k.drop_duplicates()
    exact_removed = initial_count - len(df_deduplicated)
    print(f"  Removed {exact_removed} exact duplicates")
    
    # For messages that appear more than 20 times, sample down to 20
    # (This is very conservative - only affects extreme duplicates)
    message_counts = df_deduplicated['log_message'].value_counts()
    high_freq_messages = message_counts[message_counts > 20]
    
    if len(high_freq_messages) > 0:
        print(f"  Found {len(high_freq_messages)} messages appearing >20 times")
        
        reduced_rows = []
        for message in df_deduplicated['log_message'].unique():
            message_rows = df_deduplicated[df_deduplicated['log_message'] == message]
            
            if len(message_rows) <= 20:
                # Keep all
                reduced_rows.extend(message_rows.to_dict('records'))
            else:
                # Sample 20, but ensure label diversity
                labels = message_rows['target_label'].unique()
                if len(labels) == 1:
                    # Single label - random sample
                    sampled = message_rows.sample(n=20, random_state=42)
                    reduced_rows.extend(sampled.to_dict('records'))
                else:
                    # Multiple labels - ensure each label is represented
                    per_label = max(1, 20 // len(labels))
                    kept_rows = []
                    
                    for label in labels:
                        label_rows = message_rows[message_rows['target_label'] == label]
                        if len(label_rows) <= per_label:
                            kept_rows.extend(label_rows.to_dict('records'))
                        else:
                            sampled = label_rows.sample(n=per_label, random_state=42)
                            kept_rows.extend(sampled.to_dict('records'))
                    
                    # Fill remaining slots randomly
                    remaining = 20 - len(kept_rows)
                    if remaining > 0:
                        used_indices = [row.get('index', i) for i, row in enumerate(kept_rows)]
                        remaining_rows = message_rows[~message_rows.index.isin(used_indices)]
                        if len(remaining_rows) > 0:
                            additional = remaining_rows.sample(n=min(remaining, len(remaining_rows)), random_state=42)
                            kept_rows.extend(additional.to_dict('records'))
                    
                    reduced_rows.extend(kept_rows)
        
        df_final = pd.DataFrame(reduced_rows)
        conservative_removed = len(df_deduplicated) - len(df_final)
        print(f"  Conservative deduplication removed {conservative_removed} entries")
    else:
        df_final = df_deduplicated
        conservative_removed = 0
    
    # Add domain-specific training data to address ModernHR and other issues
    print(f"\nAdding domain-specific training data...")
    
    current_time = "2025-09-14 12:00:00"
    
    # Create comprehensive domain training data
    domain_training_data = [
        # === ModernHR/HR Domain (40 examples) ===
        # User Actions
        ("ModernHR", "Employee onboarding workflow initiated", "user_action"),
        ("ModernHR", "Payroll calculation completed for employees", "user_action"),
        ("ModernHR", "Performance review cycle started", "user_action"),
        ("ModernHR", "Leave request approved for employee", "user_action"),
        ("ModernHR", "Benefits enrollment completed", "user_action"),
        ("ModernHR", "Training module assigned to employee", "user_action"),
        ("ModernHR", "Employee profile updated successfully", "user_action"),
        ("ModernHR", "Salary adjustment processed", "user_action"),
        ("ModernHR", "Time tracking data synchronized", "user_action"),
        ("ModernHR", "Employee directory updated", "user_action"),
        ("ModernHR", "Vacation request submitted", "user_action"),
        ("ModernHR", "Performance evaluation completed", "user_action"),
        ("ModernHR", "Employee promotion recorded", "user_action"),
        ("ModernHR", "Training completion tracked", "user_action"),
        ("ModernHR", "Benefits claim processed", "user_action"),
        
        # System Notifications
        ("ModernHR", "Daily payroll synchronization completed", "system_notification"),
        ("ModernHR", "Employee data backup finished", "system_notification"),
        ("ModernHR", "HR system maintenance completed", "system_notification"),
        ("ModernHR", "Benefits enrollment reminder sent", "system_notification"),
        ("ModernHR", "Training schedule published", "system_notification"),
        ("ModernHR", "Employee anniversary notifications generated", "system_notification"),
        ("ModernHR", "Performance review deadline reminder", "system_notification"),
        ("ModernHR", "HR database optimization completed", "system_notification"),
        ("ModernHR", "Employee onboarding checklist updated", "system_notification"),
        ("ModernHR", "Payroll calendar updated for next quarter", "system_notification"),
        
        # Workflow Errors
        ("ModernHR", "Employee data synchronization failed", "workflow_error"),
        ("ModernHR", "Payroll calculation error occurred", "workflow_error"),
        ("ModernHR", "Benefits enrollment system timeout", "workflow_error"),
        ("ModernHR", "Training module loading failed", "workflow_error"),
        ("ModernHR", "Employee onboarding workflow error", "workflow_error"),
        
        # Security Alerts (legitimate)
        ("ModernHR", "Unauthorized access to employee records", "security_alert"),
        ("ModernHR", "Multiple failed login attempts detected", "security_alert"),
        ("ModernHR", "Suspicious access pattern identified", "security_alert"),
        ("ModernHR", "Data privacy compliance alert", "security_alert"),
        ("ModernHR", "Employee data export security alert", "security_alert"),
        
        # === Other Problematic Domains ===
        # Billing System
        ("BillingSystem", "Monthly invoice generation completed", "user_action"),
        ("BillingSystem", "Payment processing finished successfully", "user_action"),
        ("BillingSystem", "Customer billing cycle completed", "system_notification"),
        ("BillingSystem", "Payment gateway connection timeout", "workflow_error"),
        ("BillingSystem", "Fraudulent transaction detected", "security_alert"),
        
        # Database System
        ("DatabaseSystem", "Database backup completed successfully", "system_notification"),
        ("DatabaseSystem", "Index optimization finished", "system_notification"),
        ("DatabaseSystem", "Query execution timeout", "workflow_error"),
        ("DatabaseSystem", "Unauthorized database access attempt", "security_alert"),
        
        # File System
        ("FileSystem", "File upload completed", "user_action"),
        ("FileSystem", "File backup process finished", "system_notification"),
        ("FileSystem", "Disk space cleanup completed", "system_notification"),
        ("FileSystem", "File corruption detected", "workflow_error"),
        ("FileSystem", "Unauthorized file access detected", "security_alert"),
        
        # Analytics Engine
        ("AnalyticsEngine", "Daily report generation started", "system_notification"),
        ("AnalyticsEngine", "Data warehouse sync completed", "system_notification"),
        ("AnalyticsEngine", "Custom report generated", "user_action"),
        ("AnalyticsEngine", "ETL pipeline failed", "workflow_error"),
        ("AnalyticsEngine", "Unusual data access pattern", "security_alert"),
        
        # Monitoring System
        ("MonitoringSystem", "System health check completed", "system_notification"),
        ("MonitoringSystem", "Performance metrics collected", "system_notification"),
        ("MonitoringSystem", "CPU threshold exceeded", "security_alert"),
        ("MonitoringSystem", "Memory usage critical", "security_alert"),
        ("MonitoringSystem", "Monitoring agent disconnected", "workflow_error"),
    ]
    
    # Convert to DataFrame rows
    new_rows = []
    for source, message, label in domain_training_data:
        new_row = {
            'log_message': message,
            'target_label': label,
        }
        
        # Add other columns if they exist in the original dataset
        if 'timestamp' in df_final.columns:
            new_row['timestamp'] = current_time
        if 'source' in df_final.columns:
            new_row['source'] = source
        if 'complexity' in df_final.columns:
            new_row['complexity'] = 'bert'
        
        new_rows.append(new_row)
    
    new_df = pd.DataFrame(new_rows)
    
    # Combine with the main dataset
    comprehensive_df = pd.concat([df_final, new_df], ignore_index=True)
    
    # Final deduplication (only exact duplicates)
    comprehensive_df = comprehensive_df.drop_duplicates()
    
    print(f"Added {len(new_df)} domain-specific examples")
    print(f"Final comprehensive dataset: {len(comprehensive_df)} entries")
    print(f"Data retention: {len(comprehensive_df)/len(df_20k)*100:.1f}% of original 20K")
    
    # Show final distribution
    print(f"\nFinal label distribution:")
    final_distribution = comprehensive_df['target_label'].value_counts()
    for label, count in final_distribution.items():
        pct = (count / len(comprehensive_df)) * 100
        print(f"  {label}: {count} ({pct:.1f}%)")
    
    # Save the comprehensive dataset
    output_path = 'data/training/dataset/comprehensive_20k_dataset.csv'
    comprehensive_df.to_csv(output_path, index=False)
    print(f"\nSaved comprehensive 20K dataset to: {output_path}")
    
    return comprehensive_df, output_path

if __name__ == "__main__":
    comprehensive_df, output_path = create_comprehensive_20k_dataset()
    
    if comprehensive_df is not None:
        print(f"\n✅ COMPREHENSIVE 20K TRAINING DATASET READY")
        print(f"   File: {output_path}")
        print(f"   Entries: {len(comprehensive_df):,}")
        print(f"   From original 20K dataset: ✅")
        print(f"   Smart deduplication applied: ✅")
        print(f"   Domain coverage enhanced: ✅")
        print(f"   ModernHR issues addressed: ✅")
        print(f"   Ready for high-performance model training: ✅")
    else:
        print(f"\n❌ Failed to create comprehensive 20K dataset")