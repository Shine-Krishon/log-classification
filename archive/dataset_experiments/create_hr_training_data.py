import pandas as pd
import os
from datetime import datetime

def create_hr_training_data():
    """Create proper HR training data to fix the misclassification issue."""
    
    print("🔧 CREATING HR TRAINING DATA")
    print("=" * 50)
    
    # HR-specific training data that's missing from the current dataset
    hr_training_data = [
        # User Actions - HR Operations
        ("HRSystem", "Employee onboarding workflow triggered for John Smith", "user_action"),
        ("HRSystem", "Payroll calculation completed for 250 employees", "user_action"),
        ("HRSystem", "Performance review cycle initiated for Q3", "user_action"),
        ("HRSystem", "Leave request approved for EMP001", "user_action"),
        ("HRSystem", "Benefits enrollment deadline reminder sent", "user_action"),
        ("HRSystem", "Training module completion recorded for TRAIN001", "user_action"),
        ("HRSystem", "Employee profile updated by HR admin", "user_action"),
        ("HRSystem", "New hire documentation completed", "user_action"),
        ("HRSystem", "Performance evaluation submitted", "user_action"),
        ("HRSystem", "Salary adjustment processed", "user_action"),
        ("HRSystem", "Employee termination workflow initiated", "user_action"),
        ("HRSystem", "Benefits claim submitted for review", "user_action"),
        ("HRSystem", "Training certificate generated", "user_action"),
        ("HRSystem", "Employee promotion recorded", "user_action"),
        ("HRSystem", "Vacation request submitted", "user_action"),
        
        # System Notifications - HR System Events
        ("HRSystem", "Time tracking synchronization completed", "system_notification"),
        ("HRSystem", "Employee directory updated successfully", "system_notification"),
        ("HRSystem", "Payroll system backup completed", "system_notification"),
        ("HRSystem", "HR database maintenance completed", "system_notification"),
        ("HRSystem", "Benefits enrollment period started", "system_notification"),
        ("HRSystem", "Annual performance review cycle scheduled", "system_notification"),
        ("HRSystem", "Employee data sync with external systems completed", "system_notification"),
        ("HRSystem", "HR policy documentation updated", "system_notification"),
        ("HRSystem", "Training schedule published", "system_notification"),
        ("HRSystem", "Employee handbook updated", "system_notification"),
        
        # Security Alerts - Legitimate HR Security Events
        ("HRSystem", "Compliance audit report generated", "security_alert"),
        ("HRSystem", "Access control review scheduled", "security_alert"), 
        ("HRSystem", "Unauthorized access to employee records detected", "security_alert"),
        ("HRSystem", "Data privacy violation alert triggered", "security_alert"),
        ("HRSystem", "Employee record access from unusual location", "security_alert"),
        ("HRSystem", "Sensitive HR data export detected", "security_alert"),
        ("HRSystem", "Multiple failed login attempts to HR portal", "security_alert"),
        ("HRSystem", "Admin privilege escalation in HR system", "security_alert"),
        
        # Workflow Errors - HR System Failures
        ("HRSystem", "Payroll calculation failed due to missing data", "workflow_error"),
        ("HRSystem", "Employee onboarding workflow error", "workflow_error"),
        ("HRSystem", "Benefits enrollment system timeout", "workflow_error"),
        ("HRSystem", "Performance review data sync failed", "workflow_error"),
        ("HRSystem", "Time tracking system connection error", "workflow_error"),
        ("HRSystem", "Employee record update failed", "workflow_error"),
        ("HRSystem", "Training module loading error", "workflow_error"),
        ("HRSystem", "HR report generation failed", "workflow_error"),
        
        # Deprecation Warnings - HR System Updates
        ("HRSystem", "Legacy HR module will be deprecated next quarter", "deprecation_warning"),
        ("HRSystem", "Old timesheet format will be discontinued", "deprecation_warning"),
        ("HRSystem", "Previous benefits enrollment system is obsolete", "deprecation_warning"),
    ]
    
    # Convert to DataFrame with proper structure
    current_time = datetime.now()
    enhanced_data = []
    
    for i, (source, message, label) in enumerate(hr_training_data):
        enhanced_data.append({
            'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'source': source,
            'log_message': message,
            'target_label': label,
            'complexity': 'bert'
        })
    
    hr_df = pd.DataFrame(enhanced_data)
    
    # Load existing training data
    try:
        existing_df = pd.read_csv('data/training/dataset/enhanced_synthetic_logs.csv')
        print(f"Loaded existing training data: {len(existing_df)} entries")
        
        # Combine with new HR data
        combined_df = pd.concat([existing_df, hr_df], ignore_index=True)
        print(f"Added {len(hr_df)} HR training entries")
        print(f"Total training data: {len(combined_df)} entries")
        
        # Save enhanced dataset
        output_path = 'data/training/dataset/enhanced_synthetic_logs_with_hr.csv'
        combined_df.to_csv(output_path, index=False)
        print(f"Saved enhanced dataset to: {output_path}")
        
        # Show distribution
        print("\nLabel distribution in new HR data:")
        hr_distribution = hr_df['target_label'].value_counts()
        for label, count in hr_distribution.items():
            print(f"  {label}: {count}")
            
        return output_path
        
    except Exception as e:
        print(f"Error processing training data: {e}")
        return None

if __name__ == "__main__":
    output_file = create_hr_training_data()
    if output_file:
        print(f"\n✅ HR training data created successfully!")
        print(f"Next step: Retrain the model with enhanced dataset")