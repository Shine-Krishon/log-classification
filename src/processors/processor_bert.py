import joblib
import logging
import time
from sentence_transformers import SentenceTransformer
import numpy as np
from src.utils.logger_config import get_logger
from src.core.config import config
from src.services.cache_manager import cache_result

# Set up logging
logger = get_logger(__name__)

# Global variables for model caching (simplified approach)
_bert_models = {
    'embedding': None,
    'classification': None,
    'loading_attempted': False,
    'models_loaded': False
}

def load_models():
    """Load the enhanced TF-IDF classification model."""
    global _bert_models
    
    # Check if model is already loaded
    if _bert_models['models_loaded'] and _bert_models['classification'] is not None:
        logger.debug("Enhanced classification model already loaded, using cached instance")
        return True
    
    # Don't retry if loading previously failed - but allow retry after some time
    if _bert_models['loading_attempted'] and not _bert_models['models_loaded']:
        logger.debug("Previous model loading failed, but allowing retry")
        # Reset the flag to allow retry
        _bert_models['loading_attempted'] = False
    
    _bert_models['loading_attempted'] = True
    
    try:
        logger.info(f"Loading enhanced classification model: {config.model_path}")
        
        # Try to load the enhanced model first
        import os
        model_path = config.model_path
        
        if not os.path.exists(model_path):
            logger.warning(f"Primary model not found at {model_path}, trying fallback")
            model_path = config.fallback_model_path
            
            if not os.path.exists(model_path):
                logger.error(f"No model found at {model_path}")
                return False
        
        # Load the TF-IDF pipeline model
        _bert_models['classification'] = joblib.load(model_path)
        _bert_models['embedding'] = None  # Not needed for TF-IDF model
        _bert_models['models_loaded'] = True
        
        logger.info(f"Successfully loaded enhanced classification model from {model_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load enhanced classification model: {str(e)}")
        _bert_models['models_loaded'] = False
        return False

def get_bert_embeddings(log_message):
    """Get BERT embeddings with simple caching."""
    if not load_models():
        return None
    
    try:
        embeddings = _bert_models['embedding'].encode([log_message], convert_to_numpy=True)
        return embeddings[0]  # Return single embedding vector
    except Exception as e:
        logger.error(f"Failed to generate BERT embeddings: {str(e)}")
        return None

def classify_with_bert(source, log_message):
    """
    Classify log message using the enhanced TF-IDF model (security-aware).
    
    Args:
        source (str): Log source (for compatibility with other processors)
        log_message (str): The log message to classify
        
    Returns:
        dict: Classification result with 'classification' and 'confidence' keys
    """
    start_time = time.time()
    
    if not log_message or not isinstance(log_message, str):
        logger.warning(f"Invalid input received: {type(log_message)}")
        return {
            'classification': 'unclassified',
            'confidence': 0.0,
            'processing_time': 0.0
        }
    
    # Try to load models if not already loaded
    if not load_models():
        logger.warning("Classification model not available, returning 'unclassified'")
        return {
            'classification': 'unclassified',
            'confidence': 0.0,
            'processing_time': 0.0
        }
    
    try:
        confidence_threshold = config.bert_confidence_threshold
        logger.debug(f"Classifying log message from {source} with enhanced model - Threshold: {confidence_threshold}")
        
        # Use text directly with the TF-IDF trained model
        logger.debug("Getting classification probabilities from TF-IDF model")
        probabilities = _bert_models['classification'].predict_proba([log_message])[0]
        max_probability = np.max(probabilities)
        
        logger.debug(f"Max probability: {max_probability:.3f}")
        
        if max_probability < confidence_threshold:
            logger.debug(f"Confidence below threshold ({confidence_threshold}), returning 'unclassified'")
            classification = "unclassified"
        else:
            predicted_label = _bert_models['classification'].predict([log_message])[0]
            classification = predicted_label
            logger.debug(f"Enhanced model classification completed: {predicted_label} (confidence: {max_probability:.3f})")
        
        # Simple performance tracking
        duration = time.time() - start_time
        try:
            from src.services.performance_monitor_simple import performance_monitor
            performance_monitor.record_metric({
                'function': 'classify_with_bert',
                'duration': duration,
                'timestamp': start_time,
                'metadata': {'confidence': max_probability, 'result': classification}
            })
        except:
            pass  # Don't fail if performance tracking fails
        
        return {
            'classification': classification,
            'confidence': float(max_probability),
            'processing_time': duration
        }
        
    except Exception as e:
        duration = time.time() - start_time
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
        except:
            pass
        
        logger.error(f"Error in enhanced model classification: {str(e)}", exc_info=True)
        logger.info("Returning 'unclassified' due to error")
        return {
            'classification': 'unclassified',
            'confidence': 0.0,
            'processing_time': duration
        }

def get_model_info():
    """Get information about loaded models."""
    return {
        'classification_model_loaded': _bert_models['classification'] is not None,
        'models_loaded': _bert_models['models_loaded'],
        'model_type': 'Enhanced TF-IDF Pipeline',
        'model_path': config.model_path,
        'fallback_path': config.fallback_model_path,
        'available_categories': list(config.classification_categories.keys())
    }


if __name__ == "__main__":
    logs = [
        "alpha.osapi_compute.wsgi.server - 12.10.11.1 - API returned 404 not found error",
        "GET /v2/3454/servers/detail HTTP/1.1 RCODE   404 len: 1583 time: 0.1878400",
        "System crashed due to drivers errors when restarting the server",
        "Hey bro, chill ya!",
        "Multiple login failures occurred on user 6454 account",
        "Server A790 was restarted unexpectedly during the process of data transfer"
    ]
    for log in logs:
        label = classify_with_bert(log)
        print(log, "->", label)
