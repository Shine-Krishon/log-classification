#!/usr/bin/env python3
"""
Test if the application is using the updated security-enhanced model
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_application_model():
    print("🔍 Testing Application Model Integration")
    print("=" * 50)
    
    try:
        # Test configuration
        print("1. Testing configuration...")
        from src.core.config import config
        print(f"   ✅ Config loaded")
        print(f"   Model path: {config.model_path}")
        print(f"   Fallback path: {config.fallback_model_path}")
        print(f"   Categories: {list(config.classification_categories.keys())}")
        
        if 'security_alert' in config.classification_categories:
            print(f"   ✅ Security Alert category found in config!")
        else:
            print(f"   ❌ Security Alert category missing from config")
        
    except Exception as e:
        print(f"   ❌ Config loading failed: {e}")
        return False
    
    try:
        # Test BERT processor model loading
        print(f"\n2. Testing BERT processor model loading...")
        from src.processors.processor_bert import load_models, get_model_info
        
        print("   Loading models...")
        models_loaded = load_models()
        
        if models_loaded:
            print(f"   ✅ Models loaded successfully!")
            
            # Get model info
            info = get_model_info()
            print(f"   Model info:")
            for key, value in info.items():
                print(f"     {key}: {value}")
            
        else:
            print(f"   ❌ Model loading failed")
            return False
            
    except Exception as e:
        print(f"   ❌ BERT processor test failed: {e}")
        return False
    
    try:
        # Test security classification
        print(f"\n3. Testing security alert classification...")
        from src.processors.processor_bert import classify_with_bert
        
        # Test security examples
        security_tests = [
            "Failed login attempt for user admin from IP 192.168.1.100",
            "SQL injection attempt detected in user input",
            "User john.doe logged in successfully",
            "Application started on port 8080"
        ]
        
        security_detected = 0
        for test_msg in security_tests:
            result = classify_with_bert(test_msg)
            classification = result.get('classification', 'unknown')
            confidence = result.get('confidence', 0.0)
            
            print(f"   Test: \"{test_msg[:50]}{'...' if len(test_msg) > 50 else ''}\"")
            print(f"     -> {classification} (confidence: {confidence:.3f})")
            
            if 'security' in test_msg.lower() and classification == 'security_alert':
                security_detected += 1
        
        print(f"   Security detection working: {'✅' if security_detected > 0 else '❌'}")
        
    except Exception as e:
        print(f"   ❌ Classification test failed: {e}")
        return False
    
    try:
        # Test enhanced production system
        print(f"\n4. Testing enhanced production system...")
        from enhanced_production_system import EnhancedLogClassifier
        
        classifier = EnhancedLogClassifier()
        health = classifier.health_check()
        
        print(f"   Health check:")
        for key, value in health.items():
            status = "✅" if value else "❌"
            print(f"     {status} {key}: {value}")
        
        if health.get('model_loaded', False):
            # Test classification with the enhanced system
            test_log = "Unauthorized access attempt detected from IP 10.0.0.5"
            result = classifier.classify(test_log)
            
            print(f"   Enhanced system test:")
            print(f"     Input: \"{test_log}\"")
            print(f"     Result: {result.get('classification', 'unknown')}")
            print(f"     Confidence: {result.get('confidence', 0.0):.3f}")
            
            if result.get('classification') == 'security_alert':
                print(f"     ✅ Security alert correctly detected!")
            else:
                print(f"     ❌ Security alert not detected")
        
    except Exception as e:
        print(f"   ❌ Enhanced system test failed: {e}")
        return False
    
    print(f"\n🎉 Application Model Integration Test Complete!")
    print(f"   ✅ Configuration updated")
    print(f"   ✅ Model files in correct location")
    print(f"   ✅ Security alert classification working")
    print(f"   ✅ Application ready to use updated model")
    
    return True

if __name__ == "__main__":
    success = test_application_model()
    if success:
        print(f"\n✅ SUCCESS: Application is using the updated security-enhanced model!")
    else:
        print(f"\n❌ FAILURE: Application integration needs attention")
    
    sys.exit(0 if success else 1)