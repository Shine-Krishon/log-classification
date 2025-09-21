#!/usr/bin/env python3
"""
Force reset of the enhanced classifier to pick up new model.
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and reset the classifier
from enhanced_production_system import reset_classifier, get_classifier
from processor_bert_enhanced import MODEL_PATHS, find_best_model

print("=== RESETTING ENHANCED CLASSIFIER ===")

# Reset the global instance
reset_classifier()
print("✅ Global classifier instance reset")

# Show which model will be loaded
print(f"Next model to be loaded: {find_best_model()}")

# Initialize with new model
classifier = get_classifier()
print("✅ Enhanced classifier reinitialized with new model")
print(f"Model info: {classifier.model_info}")