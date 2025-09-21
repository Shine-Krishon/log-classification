#!/usr/bin/env python3
"""
Quick test script to check BERT model loading functionality.
"""
import sys
import os
import logging

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_bert_loading():
    """Test BERT model loading and basic functionality."""
    print("🔍 Testing BERT Model Loading...")
    print("-" * 50)
    
    try:
        # Test configuration loading
        print("1. Loading configuration...")
        from src.core.config import config
        print(f"   ✅ Config loaded - BERT model: {config.bert_model_name}")
        print(f"   ✅ Model path: {config.model_path}")
        print(f"   ✅ Model file exists: {os.path.exists(config.model_path)}")
        
        # Test BERT processor import
        print("\n2. Importing BERT processor...")
        from src.processors.processor_bert import load_models, classify_with_bert, get_model_info
        print("   ✅ BERT processor imported successfully")
        
        # Test model loading
        print("\n3. Loading BERT models...")
        loading_result = load_models()
        print(f"   ✅ Model loading result: {loading_result}")
        
        # Get model info
        print("\n4. Checking model status...")
        model_info = get_model_info()
        for key, value in model_info.items():
            print(f"   📊 {key}: {value}")
        
        # Test classification if models loaded
        if loading_result:
            print("\n5. Testing classification...")
            test_message = "ERROR: Database connection failed"
            result = classify_with_bert("TestSource", test_message)
            print(f"   ✅ Test classification result: '{result}'")
            print(f"   📝 Input: '{test_message}'")
        else:
            print("\n❌ Models failed to load - skipping classification test")
            
        return loading_result
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bert_loading()
    print("\n" + "=" * 50)
    if success:
        print("🎉 BERT model testing completed successfully!")
    else:
        print("⚠️  BERT model testing failed - check logs above for details")
    print("=" * 50)