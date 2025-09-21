#!/usr/bin/env python3
"""
Test which model the enhanced classifier will actually load.
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test the model finding function
from processor_bert_enhanced import find_best_model, MODEL_PATHS

print("=== TESTING MODEL PRIORITY ===")
print(f"Model search order:")
for i, path in enumerate(MODEL_PATHS, 1):
    exists = "✅" if os.path.exists(path) else "❌"
    print(f"  {i}. {path} {exists}")

print(f"\nSelected model: {find_best_model()}")

# Check model sizes
for path in MODEL_PATHS:
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"  {path}: {size:,} bytes ({size/1024:.1f} KB)")