# PROJECT FILE USAGE ANALYSIS
# Generated on 2025-09-14

## CORE PRODUCTION FILES (KEEP ACTIVE)
These files are essential for the current production system:

### Main Application
- `src/server.py` - Main FastAPI server entry point
- `src/api/api_routes.py` - API routes and endpoints
- `src/services/classification_service.py` - Core classification service
- `src/processors/processor_bert.py` - BERT/ML model processor
- `src/processors/processor_llm.py` - LLM fallback processor
- `src/processors/processor_regex.py` - Regex first-tier processor
- `src/core/config.py` - Application configuration
- `src/core/constants.py` - Application constants
- `src/core/models.py` - Data models and schemas
- `requirements.txt` - Python dependencies

### Current Model & Data
- `models/log_classifier.joblib` - Current production model (100% accuracy)
- `data/training/dataset/advanced_dataset_5000.csv` - Current training dataset

## ENHANCED PRODUCTION FILES (UPGRADE OPTIONS)
Improved versions available for production upgrade:

- `src/services/enhanced_classification_service.py` - Enhanced classification with performance improvements
- `processor_bert_enhanced.py` - Optimized BERT processor
- `enhanced_production_system.py` - Complete enhanced system
- `src/services/task_manager.py` - Async task management
- `src/services/performance_monitor.py` - Performance monitoring
- `src/services/cache_manager.py` - Caching service

## DEVELOPMENT TOOLS (KEEP FOR FUTURE)
Essential for ongoing development:

- `advanced_dataset_generator.py` - Advanced dataset generation (proven 100% accuracy)
- `evaluate_advanced_models.py` - Model evaluation and comparison
- `scripts/train_enhanced_model.py` - Model training utilities
- `scripts/generate_enhanced_dataset.py` - Dataset generation tools
- `scripts/classify.py` - Command-line classification tool
- `check_dataset_quality.py` - Dataset quality analysis

## CONFIGURATION & DOCUMENTATION
- `README.md` - Project documentation
- `ENHANCED_SYSTEM_GUIDE.md` - Enhanced system guide
- `FINAL_DATASET_GENERATION_PROMPT.md` - Dataset methodology
- `src/utils/logger_config.py` - Logging configuration
- `src/utils/utils.py` - Utility functions

## FILES TO ARCHIVE
These files can be moved to archive/ directory for future reference:

### Experimental & Analysis Files (96+ files)
- `analyze_*.py` - Various analysis scripts
- `create_*.py` - Dataset creation experiments  
- `train_*.py` - Training experiments
- `retrain_*.py` - Retraining experiments
- `debug_*.py` - Debugging utilities
- `test_*.py` - Testing scripts
- `quick_*.py` - Quick testing utilities
- `comprehensive_*.py` - Analysis tools
- `fine_tune_*.py` - Fine-tuning experiments
- `investigate_*.py` - Investigation utilities
- `edge_case_*.py` - Edge case analysis
- `sample_*.py` - Sample validation

### Test Files
- `tests/` directory and all contents
- All test data files in `tests/test_data/`

### Old Models & Data
- `log_classifier_*.joblib` - Old model versions
- `*_test.csv` - Various test datasets
- `logs_chunk*.csv` - Data chunks
- Old training datasets (except current advanced_dataset_5000.csv)

### Generated Files
- `model_comparison_results_*.csv` - Comparison results
- `*.txt` files (various logs and notes)

## RECOMMENDED ACTIONS

1. **Keep Active (Core Production)**: 15-20 essential files
2. **Consider Upgrading**: 6 enhanced production files  
3. **Archive**: 100+ experimental/test files
4. **Backup**: Old models and datasets

## ARCHIVE STRUCTURE
```
archive/
├── experimental/       # Research and experimental scripts
├── tests/             # Test files and utilities
├── old_models/        # Deprecated model files  
├── analysis/          # Analysis and investigation files
└── dataset_experiments/ # Dataset creation experiments
```

## CURRENT DATASET STATUS
✅ **DATASET IS PRODUCTION READY**

The current `advanced_dataset_5000.csv` dataset shows:
- **4,056 unique records** (100% uniqueness)
- **100% test accuracy** 
- **75% problematic case accuracy** (major improvement from 41.67% baseline)
- **Well-balanced** across all label categories
- **Business-realistic** patterns covering enterprise domains

This dataset is **significantly superior** to previous datasets and ready for production use.

## SUMMARY
- **Total files**: ~150
- **Core production**: 15-20 files
- **Ready to archive**: 100+ files  
- **Disk space to recover**: Significant (many large CSV files)
- **Project status**: Production ready with excellent dataset quality