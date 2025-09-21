"""
Enhanced BERT processor using the new high-performance 20K trained model.
This processor integrates TF-IDF + Random Forest for superior accuracy.
"""
import joblib
import os
import time
import numpy as np
from pathlib import Path
from sklearn.pipeline import Pipeline
from src.utils.logger_config import get_logger

# Set up logging
logger = get_logger(__name__)

# Global model cache
_model_cache = {
    'model': None,
    'model_loaded': False,
    'model_path': None,
    'loading_attempted': False,
    'load_time': None
}

# Model paths (priority order - enhanced model first for accuracy)
MODEL_PATHS = [
    "models/enhanced_log_classifier.joblib",  # PRIORITY #1: Enhanced model (80% accuracy on test cases)
    "models/log_classifier.joblib",  # 5K dataset model (60% accuracy, backup)
    "models/advanced_log_classifier_20250914_113515.joblib",  # Advanced 5K model alternative
    "log_classifier_with_security_alerts.joblib",  # Enhanced model with security alerts
    "log_classifier_20k_random_forest.joblib",  # Legacy 20K model without security
    "log_classifier_20k_logistic_regression.joblib",  # Alternative 20K model
    "improved_log_classifier.joblib"  # Improved model fallback
]

def find_best_model():
    """Find the best available model in priority order (updated for 5K model priority)."""
    for model_path in MODEL_PATHS:
        if os.path.exists(model_path):
            logger.info(f"Found model: {model_path}")
            return model_path
    
    logger.error("No classification model found!")
    return None

def load_model():
    """Load the best available classification model with caching."""
    global _model_cache
    
    # Return cached model if available
    if _model_cache['model_loaded'] and _model_cache['model'] is not None:
        logger.debug("Using cached model instance")
        return True
    
    # Don't retry immediately if loading failed recently
    if _model_cache['loading_attempted'] and not _model_cache['model_loaded']:
        logger.debug("Previous model loading failed, allowing retry")
    
    _model_cache['loading_attempted'] = True
    start_time = time.time()
    
    try:
        model_path = find_best_model()
        if not model_path:
            logger.error("No model file found")
            return False
        
        logger.info(f"Loading classification model from: {model_path}")
        _model_cache['model'] = joblib.load(model_path)
        _model_cache['model_path'] = model_path
        _model_cache['model_loaded'] = True
        _model_cache['load_time'] = time.time() - start_time
        
        # Log model information
        model_type = type(_model_cache['model']).__name__
        if hasattr(_model_cache['model'], 'named_steps'):
            steps = list(_model_cache['model'].named_steps.keys())
            logger.info(f"Loaded pipeline model with steps: {steps}")
        else:
            logger.info(f"Loaded model type: {model_type}")
        
        logger.info(f"Model loaded successfully in {_model_cache['load_time']:.2f} seconds")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}", exc_info=True)
        _model_cache['model'] = None
        _model_cache['model_loaded'] = False
        return False

def classify_with_bert(log_message, source=None):
    """
    Classify log message using the new high-performance 20K model.
    
    Args:
        log_message (str): The log message to classify
        source (str): Log source (optional, for compatibility)
        
    Returns:
        str: Classification label or "unclassified"
    """
    start_time = time.time()
    
    # Input validation
    if not log_message or not isinstance(log_message, str):
        logger.warning(f"Invalid input received: {type(log_message)}")
        return "unclassified"
    
    # Load model if needed
    if not load_model():
        logger.warning("Classification model not available, returning 'unclassified'")
        return "unclassified"
    
    try:
        logger.debug(f"Classifying log message: {log_message[:100]}...")
        
        # Get prediction from the model
        prediction = _model_cache['model'].predict([log_message])[0]
        
        # Get prediction confidence if available
        confidence = None
        try:
            probabilities = _model_cache['model'].predict_proba([log_message])[0]
            confidence = np.max(probabilities)
        except AttributeError:
            # Model doesn't support predict_proba
            confidence = 1.0  # Assume high confidence for deterministic models
        
        duration = time.time() - start_time
        
        logger.debug(f"Classification completed: {prediction} (confidence: {confidence:.3f}, time: {duration:.3f}s)")
        
        # Log performance metrics
        try:
            from src.services.performance_monitor_simple import performance_monitor
            performance_monitor.record_metric({
                'function': 'classify_with_bert',
                'duration': duration,
                'timestamp': start_time,
                'metadata': {
                    'confidence': confidence,
                    'result': prediction,
                    'message_length': len(log_message),
                    'model_path': _model_cache['model_path']
                }
            })
        except Exception:
            pass  # Don't fail if performance tracking fails
        
        return prediction
        
    except Exception as e:
        duration = time.time() - start_time
        
        logger.error(f"Error in classification: {str(e)}", exc_info=True)
        
        # Record error metric
        try:
            from src.services.performance_monitor_simple import performance_monitor
            performance_monitor.record_metric({
                'function': 'classify_with_bert',
                'duration': duration,
                'timestamp': start_time,
                'error': True,
                'metadata': {'error_type': str(type(e).__name__)}
            })
        except Exception:
            pass
        
        return "unclassified"

def classify_batch(log_messages, sources=None):
    """
    Classify multiple log messages efficiently.
    
    Args:
        log_messages (list): List of log messages to classify
        sources (list): Optional list of sources (for compatibility)
        
    Returns:
        list: List of classification labels
    """
    if not log_messages:
        return []
    
    if not load_model():
        logger.warning("Model not available for batch classification")
        return ["unclassified"] * len(log_messages)
    
    start_time = time.time()
    
    try:
        logger.info(f"Starting batch classification of {len(log_messages)} messages")
        
        # Batch prediction for efficiency
        predictions = _model_cache['model'].predict(log_messages)
        
        duration = time.time() - start_time
        msgs_per_sec = len(log_messages) / duration if duration > 0 else float('inf')
        logger.info(f"Batch classification completed in {duration:.2f} seconds ({msgs_per_sec:.1f} msgs/sec)")
        
        return predictions.tolist()
        
    except Exception as e:
        logger.error(f"Error in batch classification: {str(e)}", exc_info=True)
        return ["unclassified"] * len(log_messages)

def get_model_info():
    """Get comprehensive information about the loaded model."""
    info = {
        'model_loaded': _model_cache['model_loaded'],
        'model_path': _model_cache['model_path'],
        'loading_attempted': _model_cache['loading_attempted'],
        'load_time': _model_cache['load_time'],
        'available_models': []
    }
    
    # Check which models are available
    for path in MODEL_PATHS:
        if os.path.exists(path):
            info['available_models'].append(path)
    
    # Add model-specific information
    if _model_cache['model'] is not None:
        model = _model_cache['model']
        info['model_type'] = type(model).__name__
        
        if hasattr(model, 'named_steps'):
            info['pipeline_steps'] = list(model.named_steps.keys())
            
            # Get feature info from TF-IDF if available
            if 'tfidf' in model.named_steps:
                tfidf = model.named_steps['tfidf']
                info['vocabulary_size'] = len(tfidf.vocabulary_) if hasattr(tfidf, 'vocabulary_') else 'unknown'
                info['max_features'] = getattr(tfidf, 'max_features', 'unknown')
                info['ngram_range'] = getattr(tfidf, 'ngram_range', 'unknown')
            
            # Get classifier info
            if 'rf' in model.named_steps:
                rf = model.named_steps['rf']
                info['n_estimators'] = getattr(rf, 'n_estimators', 'unknown')
                info['classes'] = getattr(rf, 'classes_', []).tolist() if hasattr(rf, 'classes_') else []
            elif 'lr' in model.named_steps:
                lr = model.named_steps['lr']
                info['classes'] = getattr(lr, 'classes_', []).tolist() if hasattr(lr, 'classes_') else []
    
    return info

def get_model_performance_stats():
    """Get performance statistics for the loaded model."""
    if not _model_cache['model_loaded']:
        return {"error": "No model loaded"}
    
    try:
        from src.services.performance_monitor_simple import performance_monitor
        return performance_monitor.get_function_stats('classify_with_bert')
    except Exception:
        return {"error": "Performance monitoring not available"}

# Backward compatibility
def classify_with_bert_legacy(source, log_message):
    """Legacy function signature for backward compatibility."""
    return classify_with_bert(log_message, source)

if __name__ == "__main__":
    # Test the enhanced processor
    test_logs = [
        "User login failed: invalid password for admin",
        "Database connection timeout after 30 seconds", 
        "API endpoint /v1/data deprecated, use /v2/data instead",
        "Memory usage exceeded 90% threshold",
        "Two-factor authentication enabled for user john.doe",
        "Payment processing completed successfully",
        "SSL certificate will expire in 7 days",
        "File upload failed: size limit exceeded",
        "Cache miss: key 'user_session_12345' not found",
        "Unknown error occurred during processing"
    ]
    
    print("=== Enhanced BERT Processor Test ===")
    print(f"Model info: {get_model_info()}")
    print("\nClassifying test messages:")
    print("-" * 60)
    
    for log in test_logs:
        label = classify_with_bert(log)
        print(f"{label:<20} | {log}")
    
    print("-" * 60)
    print(f"Performance stats: {get_model_performance_stats()}")