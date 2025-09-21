import os
import shutil
from pathlib import Path

def organize_project_files():
    """Organize project files by moving them to appropriate archive directories."""
    
    print("🗂️ ORGANIZING PROJECT FILES")
    print("=" * 50)
    
    root_dir = Path(".")
    archive_dir = root_dir / "archive"
    
    # Ensure archive directories exist
    archive_dirs = {
        'experimental': archive_dir / "experimental",
        'analysis': archive_dir / "analysis", 
        'dataset_experiments': archive_dir / "dataset_experiments",
        'old_models': archive_dir / "old_models"
    }
    
    for dir_path in archive_dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    moved_files = []
    
    # Define file patterns and their destinations
    file_moves = [
        # Analysis files
        ("analyze_*.py", "analysis"),
        ("investigate_*.py", "analysis"),
        ("comprehensive_*.py", "analysis"),
        ("edge_case_*.py", "analysis"),
        ("check_*.py", "analysis"),
        
        # Dataset experiments  
        ("create_*.py", "dataset_experiments"),
        ("dataset_*.py", "dataset_experiments"),
        ("fine_tune_*.py", "dataset_experiments"),
        ("generate_*.py", "dataset_experiments"),
        ("sample_*.py", "dataset_experiments"),
        
        # Training experiments
        ("train_*.py", "experimental"),
        ("retrain_*.py", "experimental"), 
        ("quick_*.py", "experimental"),
        ("debug_*.py", "experimental"),
        ("test_*.py", "experimental"),
        
        # Old models (but keep the current production model)
        ("log_classifier_*.joblib", "old_models"),
        ("*_model.joblib", "old_models"),
    ]
    
    # Get all Python files in root directory
    py_files = list(root_dir.glob("*.py"))
    
    # Move files based on patterns
    for file_path in py_files:
        if file_path.name in [
            "server.py", "main.py", "advanced_dataset_generator.py", 
            "evaluate_advanced_models.py", "analyze_project_usage.py",
            "PROJECT_FILE_ANALYSIS.md"
        ]:
            continue  # Keep important files
            
        moved = False
        for pattern, dest_category in file_moves:
            if match_pattern(file_path.name, pattern):
                dest_dir = archive_dirs[dest_category]
                dest_path = dest_dir / file_path.name
                
                try:
                    if not dest_path.exists():
                        shutil.move(str(file_path), str(dest_path))
                        moved_files.append((str(file_path), str(dest_path)))
                        print(f"✅ Moved: {file_path.name} → archive/{dest_category}/")
                        moved = True
                        break
                except Exception as e:
                    print(f"❌ Error moving {file_path.name}: {e}")
        
        if not moved and should_archive_file(file_path.name):
            # Move to experimental as default
            dest_path = archive_dirs['experimental'] / file_path.name
            try:
                if not dest_path.exists():
                    shutil.move(str(file_path), str(dest_path))
                    moved_files.append((str(file_path), str(dest_path)))
                    print(f"✅ Moved: {file_path.name} → archive/experimental/")
            except Exception as e:
                print(f"❌ Error moving {file_path.name}: {e}")
    
    # Move old model files
    model_files = list(root_dir.glob("*.joblib"))
    for model_file in model_files:
        if model_file.name != "log_classifier.joblib":  # Keep current production model
            dest_path = archive_dirs['old_models'] / model_file.name
            try:
                if not dest_path.exists():
                    shutil.move(str(model_file), str(dest_path))
                    moved_files.append((str(model_file), str(dest_path)))
                    print(f"✅ Moved: {model_file.name} → archive/old_models/")
            except Exception as e:
                print(f"❌ Error moving {model_file.name}: {e}")
    
    # Move CSV test files (but keep important datasets)
    csv_files = list(root_dir.glob("*.csv"))
    important_csvs = ["advanced_dataset_5000.csv"]
    
    for csv_file in csv_files:
        if any(important in csv_file.name for important in important_csvs):
            continue  # Keep important datasets
            
        if any(test_term in csv_file.name.lower() for test_term in ['test', 'chunk', 'result']):
            dest_path = archive_dirs['experimental'] / csv_file.name
            try:
                if not dest_path.exists():
                    shutil.move(str(csv_file), str(dest_path))
                    moved_files.append((str(csv_file), str(dest_path)))
                    print(f"✅ Moved: {csv_file.name} → archive/experimental/")
            except Exception as e:
                print(f"❌ Error moving {csv_file.name}: {e}")
    
    print(f"\n📊 ORGANIZATION SUMMARY")
    print(f"Total files moved: {len(moved_files)}")
    
    # Count files in each archive category
    for category, dir_path in archive_dirs.items():
        file_count = len(list(dir_path.glob("*")))
        print(f"  {category}: {file_count} files")
    
    # Show remaining files in root
    remaining_py = len(list(root_dir.glob("*.py")))
    remaining_csv = len(list(root_dir.glob("*.csv"))) 
    remaining_joblib = len(list(root_dir.glob("*.joblib")))
    
    print(f"\n📁 REMAINING IN ROOT:")
    print(f"  Python files: {remaining_py}")
    print(f"  CSV files: {remaining_csv}")
    print(f"  Model files: {remaining_joblib}")
    
    return moved_files

def match_pattern(filename, pattern):
    """Check if filename matches a glob-style pattern."""
    import fnmatch
    return fnmatch.fnmatch(filename, pattern)

def should_archive_file(filename):
    """Check if a file should be archived based on its name."""
    archive_indicators = [
        'test_', 'debug_', 'quick_', 'temp_', 'old_', 'backup_',
        'experiment', 'trial', 'attempt', 'prototype'
    ]
    
    return any(indicator in filename.lower() for indicator in archive_indicators)

if __name__ == "__main__":
    try:
        moved_files = organize_project_files()
        print(f"\n✅ PROJECT ORGANIZATION COMPLETE!")
        print(f"Files have been organized into archive directories.")
        print(f"Core production files remain in the root directory.")
    except Exception as e:
        print(f"❌ Error during organization: {e}")