import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def analyze_modernhr_misclassification():
    """Analyze the ModernHR misclassification issue."""
    
    print("🔍 ANALYZING MODERNHR MISCLASSIFICATION")
    print("=" * 60)
    
    # Load the results
    try:
        results_df = pd.read_csv('resources/output.csv')
        print(f"Loaded {len(results_df)} classification results")
    except Exception as e:
        print(f"Error loading results: {e}")
        return
    
    # Filter ModernHR entries
    modernhr_data = results_df[results_df['source'] == 'ModernHR'].copy()
    print(f"Found {len(modernhr_data)} ModernHR entries")
    print()
    
    # Analyze current classifications
    print("CURRENT MODERNHR CLASSIFICATIONS:")
    print("-" * 40)
    for _, row in modernhr_data.iterrows():
        message = row['log_message']
        classification = row['target_label']
        
        # Determine what it should actually be
        if any(word in message.lower() for word in ['employee', 'payroll', 'leave', 'benefits', 'training', 'performance']):
            expected = "user_action"  # HR operations are user actions
        elif any(word in message.lower() for word in ['audit', 'compliance', 'access control']):
            expected = "security_alert"  # These are legitimate security items
        elif any(word in message.lower() for word in ['sync', 'directory updated', 'tracking']):
            expected = "system_notification"  # System operations
        else:
            expected = "user_action"  # Default for HR operations
        
        status = "✅" if classification == expected else "❌"
        print(f"{status} '{message}'")
        print(f"   Got: {classification}, Expected: {expected}")
        print()
    
    # Summary of misclassifications
    print("CLASSIFICATION SUMMARY:")
    print("-" * 40)
    classification_counts = modernhr_data['target_label'].value_counts()
    for label, count in classification_counts.items():
        percentage = (count / len(modernhr_data)) * 100
        print(f"{label}: {count} ({percentage:.1f}%)")
    
    return modernhr_data

def test_individual_modernhr_messages():
    """Test individual ModernHR messages through the classification pipeline."""
    
    print("\n🧪 TESTING INDIVIDUAL MODERNHR MESSAGES")
    print("=" * 60)
    
    # Import classification functions
    try:
        from src.processors.processor_regex import classify_with_regex
        from enhanced_production_system import classify_log_message
        
        modernhr_messages = [
            "Employee onboarding workflow triggered",
            "Payroll calculation completed for 250 employees", 
            "Performance review cycle initiated",
            "Leave request approved for EMP001",
            "Benefits enrollment deadline reminder sent",
            "Training module completion recorded",
            "Compliance audit report generated",
            "Employee directory updated",
            "Access control review scheduled"
        ]
        
        print("Testing each message through the pipeline:")
        print()
        
        for message in modernhr_messages:
            # Test regex first
            regex_result = classify_with_regex("test", message)
            
            # Test enhanced model
            try:
                enhanced_result = classify_log_message(message)
            except Exception as e:
                enhanced_result = f"ERROR: {e}"
            
            print(f"Message: '{message}'")
            print(f"   Regex: {regex_result}")
            print(f"   Enhanced: {enhanced_result}")
            
            # Expected classification
            if any(word in message.lower() for word in ['employee', 'payroll', 'leave', 'benefits', 'training', 'performance']):
                expected = "user_action"
            elif any(word in message.lower() for word in ['audit', 'compliance', 'access control']):
                expected = "security_alert"
            else:
                expected = "system_notification"
                
            print(f"   Expected: {expected}")
            print()
            
    except Exception as e:
        print(f"Error testing pipeline: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    modernhr_data = analyze_modernhr_misclassification()
    test_individual_modernhr_messages()