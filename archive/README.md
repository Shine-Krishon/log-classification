# Archive Organization Guide

This directory contains files that are not actively used in production but are kept for future reference and development.

## Directory Structure

### `/experimental/`
Research and experimental scripts that were used during development but are not part of the core system.

### `/analysis/` 
Analysis and investigation files used to understand data patterns, model performance, and system behavior.

### `/dataset_experiments/`
Various experiments in dataset creation and enhancement. The successful approach is now in `advanced_dataset_generator.py`.

### `/old_models/`
Previous model versions that have been superseded by the current production model.

## Current Production Status

The main project now uses:
- **Model**: `models/log_classifier.joblib` (100% accuracy)
- **Dataset**: `data/training/dataset/advanced_dataset_5000.csv` (4,056 unique records)
- **Core Files**: See PROJECT_FILE_ANALYSIS.md for complete list

## Usage

These archived files can be:
1. Referenced for understanding development history
2. Used as starting points for future experiments  
3. Restored if needed for debugging or comparison
4. Safely deleted if disk space is needed (after backup)

## Last Updated
September 14, 2025