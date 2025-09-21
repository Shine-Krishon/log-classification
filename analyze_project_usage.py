import os
import re
from collections import defaultdict
import datetime

def analyze_project_file_usage():
    """Analyze the entire project to categorize files by usage and importance."""
    
    print("🔍 PROJECT FILE USAGE ANALYSIS")
    print("=" * 60)
    
    # Define core production files (actively used in production)
    core_production_files = {
        # Main application files
        'src/server.py': 'Main FastAPI server - core application entry point',
        'src/api/api_routes.py': 'API routes and endpoints - core functionality', 
        'src/services/classification_service.py': 'Main classification service logic',
        'src/processors/processor_bert.py': 'BERT/ML model processor - core classification',
        'src/processors/processor_llm.py': 'LLM processor - fallback classification',
        'src/processors/processor_regex.py': 'Regex processor - first-tier classification',
        'src/core/config.py': 'Application configuration management',
        'src/core/constants.py': 'Application constants and enums',
        'requirements.txt': 'Python dependencies specification',
        
        # Current trained model
        'models/log_classifier.joblib': 'Production ML model - currently deployed',
        
        # Current dataset
        'data/training/dataset/advanced_dataset_5000.csv': 'Current training dataset - 100% accuracy'
    }
    
    # Enhanced/alternative production files (improved versions)
    enhanced_production_files = {
        'src/services/enhanced_classification_service.py': 'Enhanced classification service with performance improvements',
        'processor_bert_enhanced.py': 'Enhanced BERT processor with optimizations',
        'enhanced_production_system.py': 'Complete enhanced production system',
        'src/services/task_manager.py': 'Async task management for enhanced system',
        'src/services/performance_monitor.py': 'Performance monitoring service',
        'src/services/cache_manager.py': 'Caching service for performance',
    }
    
    # Development and testing utilities (kept for future development)
    development_files = {
        'scripts/train_enhanced_model.py': 'Model training script',
        'scripts/generate_enhanced_dataset.py': 'Dataset generation utilities',
        'scripts/classify.py': 'Command-line classification tool',
        'advanced_dataset_generator.py': 'Advanced dataset generation - proven 100% accuracy',
        'evaluate_advanced_models.py': 'Model evaluation and comparison tool',
        'check_dataset_quality.py': 'Dataset quality analysis tool',
        'test_current_model.py': 'Current model testing utilities',
    }
    
    # Configuration and documentation
    config_docs_files = {
        'README.md': 'Project documentation',
        'ENHANCED_SYSTEM_GUIDE.md': 'Enhanced system documentation',
        'FINAL_DATASET_GENERATION_PROMPT.md': 'Dataset generation methodology',
        'src/core/models.py': 'Data models and schemas',
        'src/utils/logger_config.py': 'Logging configuration',
        'src/utils/utils.py': 'Utility functions',
    }
    
    # Test files and test data
    test_files = {
        'tests/': 'All test files and test data',
        'test_*.py': 'Various testing scripts - can be archived',
        'tests/test_data/': 'Test datasets for validation'
    }
    
    # Experimental and analysis files (can be archived)
    experimental_files = {
        'analyze_*.py': 'Analysis scripts for various investigations',
        'create_*.py': 'Dataset creation experiments',
        'fine_tune_*.py': 'Model fine-tuning experiments', 
        'train_*.py': 'Various training experiments',
        'retrain_*.py': 'Model retraining experiments',
        'debug_*.py': 'Debugging utilities',
        'quick_*.py': 'Quick testing utilities',
        'comprehensive_*.py': 'Comprehensive analysis tools',
        'edge_case_*.py': 'Edge case analysis',
        'sample_*.py': 'Sample validation tools',
        'investigate_*.py': 'Investigation utilities',
        'dataset_*.py': 'Dataset analysis tools'
    }
    
    # Get all files in the project
    all_files = []
    root_dir = os.getcwd()
    
    for root, dirs, files in os.walk(root_dir):
        # Skip certain directories
        skip_dirs = {'__pycache__', '.git', 'node_modules', '.vscode', 'venv', 'env'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if not file.startswith('.') and not file.endswith('.pyc'):
                rel_path = os.path.relpath(os.path.join(root, file), root_dir).replace('\\', '/')
                all_files.append(rel_path)
    
    # Categorize files
    categorized_files = {
        'core_production': [],
        'enhanced_production': [], 
        'development_tools': [],
        'config_docs': [],
        'test_files': [],
        'experimental': [],
        'data_files': [],
        'model_files': [],
        'uncategorized': []
    }
    
    # Helper function to check if file matches pattern
    def matches_pattern(filename, pattern):
        if '*' in pattern:
            regex_pattern = pattern.replace('*', '.*')
            return bool(re.match(regex_pattern, filename))
        return filename == pattern or filename.endswith(pattern)
    
    # Categorize each file
    for file_path in all_files:
        categorized = False
        
        # Check core production files
        for core_file, desc in core_production_files.items():
            if matches_pattern(file_path, core_file):
                categorized_files['core_production'].append((file_path, desc))
                categorized = True
                break
        
        if categorized:
            continue
            
        # Check enhanced production files
        for enhanced_file, desc in enhanced_production_files.items():
            if matches_pattern(file_path, enhanced_file):
                categorized_files['enhanced_production'].append((file_path, desc))
                categorized = True
                break
        
        if categorized:
            continue
            
        # Check development files
        for dev_file, desc in development_files.items():
            if matches_pattern(file_path, dev_file):
                categorized_files['development_tools'].append((file_path, desc))
                categorized = True
                break
        
        if categorized:
            continue
            
        # Check config/docs files
        for config_file, desc in config_docs_files.items():
            if matches_pattern(file_path, config_file):
                categorized_files['config_docs'].append((file_path, desc))
                categorized = True
                break
        
        if categorized:
            continue
        
        # Check test files
        if 'test' in file_path.lower() or file_path.startswith('tests/'):
            categorized_files['test_files'].append((file_path, 'Test file'))
            categorized = True
        
        if categorized:
            continue
            
        # Check experimental files
        for exp_pattern in experimental_files.keys():
            if matches_pattern(file_path, exp_pattern):
                categorized_files['experimental'].append((file_path, experimental_files[exp_pattern]))
                categorized = True
                break
        
        if categorized:
            continue
            
        # Check data files
        if any(ext in file_path for ext in ['.csv', '.json', '.txt']) and 'data' in file_path:
            categorized_files['data_files'].append((file_path, 'Data file'))
            categorized = True
        
        if categorized:
            continue
            
        # Check model files
        if file_path.endswith('.joblib') or 'model' in file_path.lower():
            categorized_files['model_files'].append((file_path, 'Model file'))
            categorized = True
        
        if categorized:
            continue
            
        # Uncategorized
        categorized_files['uncategorized'].append((file_path, 'Needs classification'))
    
    # Generate report
    print(f"\n📊 PROJECT FILE ANALYSIS RESULTS")
    print(f"Total files analyzed: {len(all_files)}")
    print(f"Analysis date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    categories_info = {
        'core_production': ('🟢 CORE PRODUCTION FILES', 'Essential files currently used in production'),
        'enhanced_production': ('🔵 ENHANCED PRODUCTION FILES', 'Improved versions available for production upgrade'),
        'development_tools': ('🟡 DEVELOPMENT TOOLS', 'Utilities for development and model training'),
        'config_docs': ('📚 CONFIGURATION & DOCUMENTATION', 'Project configuration and documentation'),
        'test_files': ('🧪 TEST FILES', 'Testing utilities and test data'),
        'experimental': ('🔬 EXPERIMENTAL FILES', 'Research, analysis, and experimental code'),
        'data_files': ('📊 DATA FILES', 'Training data, test data, and other datasets'),
        'model_files': ('🤖 MODEL FILES', 'Trained models and model-related files'),
        'uncategorized': ('❓ UNCATEGORIZED', 'Files needing manual classification')
    }
    
    for category, (title, description) in categories_info.items():
        files = categorized_files[category]
        print(f"\n{title}")
        print(f"Description: {description}")
        print(f"Count: {len(files)}")
        
        if files:
            print("Files:")
            for file_path, desc in files:
                print(f"  • {file_path}")
                if desc != 'Needs classification':
                    print(f"    └─ {desc}")
    
    # Generate recommendations
    print(f"\n🎯 RECOMMENDATIONS")
    print("=" * 60)
    
    print("\n✅ KEEP ACTIVE (Core Production):")
    for file_path, desc in categorized_files['core_production']:
        print(f"  • {file_path}")
    
    print("\n🔄 CONSIDER UPGRADING TO:")
    for file_path, desc in categorized_files['enhanced_production']:
        print(f"  • {file_path}")
    
    print("\n📦 ARCHIVE BUT KEEP (Development Tools):")
    dev_files = categorized_files['development_tools'] + categorized_files['config_docs']
    for file_path, desc in dev_files:
        print(f"  • {file_path}")
    
    print("\n🗄️ ARCHIVE (Experimental & Test Files):")
    archive_files = categorized_files['experimental'] + categorized_files['test_files']
    archive_count = len(archive_files)
    print(f"Total files to archive: {archive_count}")
    
    if archive_count <= 20:  # Show all if not too many
        for file_path, desc in archive_files:
            print(f"  • {file_path}")
    else:  # Show summary if too many
        print("Summary by pattern:")
        patterns = defaultdict(int)
        for file_path, desc in archive_files:
            if file_path.startswith('test'):
                patterns['test_*.py files'] += 1
            elif 'analyze' in file_path:
                patterns['analyze_*.py files'] += 1
            elif 'create' in file_path:
                patterns['create_*.py files'] += 1
            elif 'train' in file_path:
                patterns['train_*.py files'] += 1
            elif 'debug' in file_path:
                patterns['debug_*.py files'] += 1
            else:
                patterns['other experimental files'] += 1
        
        for pattern, count in patterns.items():
            print(f"  • {count} {pattern}")
    
    # Create archive plan
    return categorized_files

def create_file_organization_plan(categorized_files):
    """Create a plan to organize files."""
    
    print(f"\n📋 FILE ORGANIZATION PLAN")
    print("=" * 60)
    
    # Create archive directory structure
    archive_structure = {
        'archive/': 'Root archive directory',
        'archive/experimental/': 'Experimental and research files',
        'archive/tests/': 'Test files and utilities', 
        'archive/old_models/': 'Deprecated model files',
        'archive/analysis/': 'Analysis and investigation files',
        'archive/dataset_experiments/': 'Dataset creation experiments'
    }
    
    print("\n📁 PROPOSED DIRECTORY STRUCTURE:")
    for dir_path, desc in archive_structure.items():
        print(f"  {dir_path} - {desc}")
    
    # File movement plan
    move_plan = []
    
    # Archive experimental files
    for file_path, desc in categorized_files['experimental']:
        if 'analyze' in file_path or 'investigate' in file_path:
            move_plan.append((file_path, 'archive/analysis/', desc))
        elif 'create' in file_path or 'dataset' in file_path:
            move_plan.append((file_path, 'archive/dataset_experiments/', desc))
        else:
            move_plan.append((file_path, 'archive/experimental/', desc))
    
    # Archive test files
    for file_path, desc in categorized_files['test_files']:
        move_plan.append((file_path, 'archive/tests/', desc))
    
    # Archive old models (keep current production model)
    for file_path, desc in categorized_files['model_files']:
        if 'log_classifier.joblib' not in file_path:  # Keep current production model
            move_plan.append((file_path, 'archive/old_models/', desc))
    
    print(f"\n📦 MOVE PLAN ({len(move_plan)} files):")
    for source, dest_dir, desc in move_plan[:10]:  # Show first 10
        print(f"  {source} → {dest_dir}")
    
    if len(move_plan) > 10:
        print(f"  ... and {len(move_plan) - 10} more files")
    
    return move_plan

if __name__ == "__main__":
    categorized_files = analyze_project_file_usage()
    move_plan = create_file_organization_plan(categorized_files)
    
    print(f"\n✨ ANALYSIS COMPLETE")
    print(f"Core production files identified and protected")
    print(f"Archive plan created for {len(move_plan)} files")
    print(f"Enhanced production files available for upgrade")