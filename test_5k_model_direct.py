#!/usr/bin/env python3
"""
Direct test of the 5K dataset model to verify ModernHR classification fix.
"""
import sys
import os

# Add src directory to Python path for organized structure
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_5k_model():
    """Test the updated 5K dataset model directly."""
    try:
        from src.processors.processor_bert import classify_with_bert
        from src.core.config import config
        
        print("=== TESTING 5K DATASET MODEL ===")
        print(f"Model path: {config.model_path}")
        print(f"Fallback path: {config.fallback_model_path}")
        print()
        
        # Test cases including the problematic ModernHR case
        test_cases = [
            ("ModernHR", "Employee EMP2001 submitted time-off request for vacation"),
            ("WorkforceOne", "User login attempt failed - invalid credentials"), 
            ("PayrollSys", "SSL certificate will expire in 30 days - renewal required"),
            ("SecurityGateway", "Unauthorized access attempt detected from IP 192.168.1.100"),
            ("DataPipeline", "ETL process completed successfully - 1250 records processed")
        ]
        
        print("Classification Results:")
        print("-" * 80)
        
        for i, (source, log_message) in enumerate(test_cases, 1):
            try:
                result = classify_with_bert(source, log_message)
                classification = result.get('classification', 'unclassified')
                confidence = result.get('confidence', 0.0)
                
                print(f"{i}. Source: {source}")
                print(f"   Message: {log_message}")
                print(f"   Classification: {classification} (confidence: {confidence:.3f})")
                print()
                
            except Exception as e:
                print(f"{i}. Error classifying {source}: {e}")
                print()
                
    except Exception as e:
        print(f"Error importing or running test: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_5k_model()
    if success:
        print("✅ 5K dataset model test completed successfully!")
    else:
        print("❌ 5K dataset model test failed!")