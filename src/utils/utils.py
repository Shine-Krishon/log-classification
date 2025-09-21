"""
Utility functions for the log classification project.
"""
import os
import pandas as pd
from typing import Tuple, List, Dict, Any
from io import StringIO
from src.utils.logger_config import get_logger
from src.core.config import config

logger = get_logger(__name__)

def validate_file_upload(filename: str, content: bytes) -> Tuple[bool, str]:
    """
    Validate uploaded file for classification.
    
    Args:
        filename (str): Name of the uploaded file
        content (bytes): File content
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Check filename
    if not filename:
        return False, "No file provided"
    
    # Check file extension
    file_extension = filename.split('.')[-1].lower()
    if file_extension not in config.allowed_file_types:
        return False, f"File must be one of: {', '.join(config.allowed_file_types)}"
    
    # Check file size
    file_size_mb = len(content) / (1024 * 1024)
    if len(content) > config.max_file_size_bytes:
        return False, f"File too large. Maximum size: {config.max_file_size_mb}MB"
    
    logger.info(f"File validation passed: {filename} ({file_size_mb:.2f}MB)")
    return True, ""

def parse_csv_content(content: bytes) -> pd.DataFrame:
    """
    Parse CSV content and validate structure.
    
    Args:
        content (bytes): CSV file content
        
    Returns:
        pd.DataFrame: Parsed DataFrame
        
    Raises:
        ValueError: If CSV is invalid or missing required columns
    """
    try:
        # Decode and parse CSV
        df = pd.read_csv(StringIO(content.decode('utf-8')))
        logger.info(f"CSV parsed successfully: {len(df)} rows, columns: {list(df.columns)}")
        
        # Validate required columns
        missing_columns = [col for col in config.required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"CSV must contain columns: {missing_columns}")
        
        # Check if empty
        if df.empty:
            raise ValueError("CSV file is empty")
        
        # Log null value warnings
        for col in config.required_columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                logger.warning(f"Found {null_count} null values in column '{col}'")
        
        return df
        
    except UnicodeDecodeError:
        raise ValueError("File must be UTF-8 encoded")
    except pd.errors.EmptyDataError:
        raise ValueError("CSV file is empty or invalid")
    except pd.errors.ParserError as e:
        raise ValueError(f"Invalid CSV format: {str(e)}")

def prepare_logs_for_classification(df: pd.DataFrame) -> List[Tuple[str, str]]:
    """
    Prepare DataFrame for classification by extracting source and message pairs.
    
    Args:
        df (pd.DataFrame): Input DataFrame with source and log_message columns
        
    Returns:
        List[Tuple[str, str]]: List of (source, log_message) tuples
    """
    logs_data = list(zip(
        df[config.required_columns[0]].fillna(''), 
        df[config.required_columns[1]].fillna('')
    ))
    
    logger.debug(f"Prepared {len(logs_data)} log entries for classification")
    return logs_data

def save_classification_results(df: pd.DataFrame, labels: List[str]) -> str:
    """
    Save classification results to output file.
    
    Args:
        df (pd.DataFrame): Original DataFrame
        labels (List[str]): Classification labels
        
    Returns:
        str: Path to output file
    """
    # Add classification labels
    df[config.target_column] = labels
    
    # Save to output file
    output_path = config.get_output_path()
    df.to_csv(output_path, index=False)
    
    logger.info(f"Classification results saved to: {output_path}")
    return output_path

def get_classification_statistics(labels: List[str]) -> Dict[str, Any]:
    """
    Generate classification statistics.
    
    Args:
        labels (List[str]): Classification labels
        
    Returns:
        Dict[str, Any]: Statistics dictionary
    """
    label_counts = {}
    for label in labels:
        label_counts[label] = label_counts.get(label, 0) + 1
    
    total = len(labels)
    stats = {
        "total_logs": total,
        "label_counts": label_counts,
        "label_percentages": {
            label: round((count / total) * 100, 2) 
            for label, count in label_counts.items()
        }
    }
    
    logger.info(f"Classification statistics: {stats}")
    return stats