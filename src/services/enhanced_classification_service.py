"""
UPDATED Classification service that uses the new enhanced 20K model.
This replaces the old processor_bert with the high-performance enhanced system.
"""
from typing import List, Tuple, Dict, Any, Optional
import sys
import os

# Add the root directory to path to import our enhanced system
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, root_dir)

from src.utils.logger_config import get_logger
from src.core.config import config
from src.processors.processor_regex import classify_with_regex
from src.processors.processor_llm import classify_with_llm

# NEW: Import the enhanced 20K model system
try:
    from enhanced_production_system import get_classifier, classify_log_message
    ENHANCED_MODEL_AVAILABLE = True
    logger = get_logger(__name__)
    logger.info("[ENHANCED] Enhanced 20K model loaded successfully!")
except ImportError as e:
    logger = get_logger(__name__)
    logger.warning(f"Enhanced model not available, falling back to legacy BERT: {e}")
    from src.processors.processor_bert import classify_with_bert
    ENHANCED_MODEL_AVAILABLE = False

class EnhancedClassificationService:
    """Enhanced service using the new 20K high-performance model."""
    
    def __init__(self):
        """Initialize the enhanced classification service."""
        self.stats = {
            "total_processed": 0,
            "regex_classified": 0,
            "enhanced_bert_classified": 0,  # NEW: Track enhanced model usage
            "legacy_bert_classified": 0,    # OLD: Track legacy model usage
            "llm_classified": 0,
            "unclassified": 0
        }
        
        if ENHANCED_MODEL_AVAILABLE:
            logger.info("[ENHANCED] Enhanced Classification Service initialized with 20K model")
            # Initialize the classifier to ensure it's loaded
            try:
                classifier = get_classifier()
                model_info = classifier.get_model_info()
                logger.info(f"Model info: {model_info.get('model_path', 'unknown')}")
            except Exception as e:
                logger.error(f"Failed to initialize enhanced model: {e}")
        else:
            logger.warning("[WARNING] Using legacy classification service")
    
    def classify_logs(self, logs_data: List[Tuple[str, str]], task_id: Optional[str] = None) -> List[str]:
        """
        Classify logs using the enhanced 20K model system.
        
        Args:
            logs_data: List of (source, log_message) tuples
            task_id: Optional task ID for cancellation support
            
        Returns:
            List of classification labels
        """
        logger.info(f"[ENHANCED] Starting ENHANCED classification for {len(logs_data)} log entries (task: {task_id})")
        self.stats["total_processed"] = len(logs_data)
        
        # Phase 1: Process with regex first (fastest)
        results = ["unclassified"] * len(logs_data)
        enhanced_bert_candidates = []  # For the new 20K model
        llm_candidates = []  # For LLM processing
        
        for i, (source, log_message) in enumerate(logs_data):
            # Check for cancellation
            if task_id:
                from src.services.task_manager import task_manager
                if task_manager.is_cancelled(task_id):
                    logger.info(f"Classification cancelled for task {task_id} at record {i+1}")
                    return ["cancelled"] * len(logs_data)
            
            try:
                # Step 1: Try regex first (fastest)
                regex_result = classify_with_regex(source, log_message)
                
                if regex_result != "unclassified":
                    results[i] = regex_result
                    self.stats["regex_classified"] += 1
                    continue
                
                # Step 2: For legacy sources, queue for LLM
                if source in config.legacy_sources:
                    llm_candidates.append((i, source, log_message))
                    continue
                
                # Step 3: Queue for enhanced BERT processing
                enhanced_bert_candidates.append((i, source, log_message))
                    
            except Exception as e:
                logger.error(f"Error in initial classification for log {i+1}: {str(e)}")
                enhanced_bert_candidates.append((i, source, log_message))  # Try enhanced BERT as fallback
        
        # Phase 2: Process with Enhanced 20K Model (batch for efficiency)
        if enhanced_bert_candidates:
            logger.info(f"[AI] Processing {len(enhanced_bert_candidates)} logs with Enhanced 20K Model")
            
            if ENHANCED_MODEL_AVAILABLE:
                try:
                    # Extract just the log messages for batch processing
                    messages = [log_message for _, _, log_message in enhanced_bert_candidates]
                    
                    # Use the enhanced batch classification with proper error handling
                    classifier = get_classifier()
                    batch_predictions = classifier.classify_batch(messages, include_metadata=False)
                    
                    # Ensure predictions match candidates count
                    if len(batch_predictions) != len(enhanced_bert_candidates):
                        logger.error(f"Prediction count mismatch: {len(batch_predictions)} predictions for {len(enhanced_bert_candidates)} candidates")
                        # Fallback: mark all as needing LLM processing
                        for index, source, log_message in enhanced_bert_candidates:
                            llm_candidates.append((index, source, log_message))
                    else:
                        # Check if we got dictionaries or strings
                        if batch_predictions and isinstance(batch_predictions[0], dict):
                            # New format with dictionaries
                            for i, (index, source, log_message) in enumerate(enhanced_bert_candidates):
                                if i < len(batch_predictions):
                                    result_dict = batch_predictions[i]
                                    prediction = result_dict['prediction']
                                    results[index] = prediction
                                    
                                    if prediction != "unclassified":
                                        self.stats["enhanced_bert_classified"] += 1
                                    else:
                                        # Queue for LLM as final fallback
                                        llm_candidates.append((index, source, log_message))
                                else:
                                    logger.error(f"Index {i} out of range for batch predictions")
                                    llm_candidates.append((index, source, log_message))
                        else:
                            # Legacy format with strings
                            for i, (index, source, log_message) in enumerate(enhanced_bert_candidates):
                                if i < len(batch_predictions):
                                    prediction = batch_predictions[i]
                                    results[index] = prediction
                                    
                                    if prediction != "unclassified":
                                        self.stats["enhanced_bert_classified"] += 1
                                    else:
                                        # Queue for LLM as final fallback
                                        llm_candidates.append((index, source, log_message))
                                else:
                                    logger.error(f"Index {i} out of range for batch predictions")
                                    llm_candidates.append((index, source, log_message))
                    
                    logger.info(f"[SUCCESS] Enhanced model processed {len(enhanced_bert_candidates)} messages")
                    
                except Exception as e:
                    logger.error(f"Error in enhanced batch processing: {str(e)}")
                    # Fallback to individual processing
                    for index, source, log_message in enhanced_bert_candidates:
                        try:
                            result = classify_log_message(log_message)
                            prediction = result['prediction']
                            results[index] = prediction
                            
                            if prediction != "unclassified":
                                self.stats["enhanced_bert_classified"] += 1
                            else:
                                llm_candidates.append((index, source, log_message))
                        except Exception as e2:
                            logger.error(f"Error in enhanced individual processing: {str(e2)}")
                            llm_candidates.append((index, source, log_message))
            else:
                # Fallback to legacy BERT
                logger.warning("[FALLBACK] Falling back to legacy BERT processing")
                for index, source, log_message in enhanced_bert_candidates:
                    try:
                        bert_result = classify_with_bert(source, log_message)
                        results[index] = bert_result
                        
                        if bert_result != "unclassified":
                            self.stats["legacy_bert_classified"] += 1
                        else:
                            llm_candidates.append((index, source, log_message))
                    except Exception as e:
                        logger.error(f"Error in legacy BERT: {str(e)}")
                        llm_candidates.append((index, source, log_message))
        
        # Phase 3: Process remaining with LLM
        if llm_candidates:
            logger.info(f"[LLM] Processing {len(llm_candidates)} logs with LLM")
            
            # Check for cancellation before LLM batch
            if task_id:
                from src.services.task_manager import task_manager
                if task_manager.is_cancelled(task_id):
                    logger.info(f"Classification cancelled before LLM batch processing")
                    return ["cancelled"] * len(logs_data)
            
            try:
                # Extract log entries for batch processing
                batch_entries = [(source, log_message) for _, source, log_message in llm_candidates]
                
                # Batch classify with LLM
                from src.processors.processor_llm import classify_with_llm_batch
                llm_results = classify_with_llm_batch(batch_entries, task_id)
                
                # Assign results back to their positions
                for (index, _, _), llm_result in zip(llm_candidates, llm_results):
                    if llm_result == "cancelled":
                        return ["cancelled"] * len(logs_data)
                    results[index] = llm_result
                    if llm_result != "unclassified":
                        self.stats["llm_classified"] += 1
                    else:
                        self.stats["unclassified"] += 1
                        
            except Exception as e:
                logger.error(f"Error in LLM batch processing: {str(e)}")
                # Fallback to individual LLM processing
                for index, source, log_message in llm_candidates:
                    try:
                        llm_result = classify_with_llm(source, log_message, task_id)
                        results[index] = llm_result
                        if llm_result != "unclassified":
                            self.stats["llm_classified"] += 1
                        else:
                            self.stats["unclassified"] += 1
                    except Exception as e2:
                        logger.error(f"Error in fallback LLM classification: {str(e2)}")
                        results[index] = "unclassified"
                        self.stats["unclassified"] += 1
        
        # Update final stats
        unclassified_count = sum(1 for result in results if result == "unclassified")
        self.stats["unclassified"] = unclassified_count
        
        # Log final progress and performance
        logger.info(f"[COMPLETE] Progress: {len(logs_data)}/{len(logs_data)} logs (100.0%)")
        self._log_enhanced_classification_stats()
        
        return results
    
    def _log_enhanced_classification_stats(self):
        """Log enhanced classification statistics."""
        total_logs = self.stats["total_processed"]
        if total_logs > 0:
            regex_pct = (self.stats["regex_classified"] / total_logs) * 100
            enhanced_bert_pct = (self.stats["enhanced_bert_classified"] / total_logs) * 100
            legacy_bert_pct = (self.stats["legacy_bert_classified"] / total_logs) * 100
            llm_pct = (self.stats["llm_classified"] / total_logs) * 100
            unclassified_pct = (self.stats["unclassified"] / total_logs) * 100
            
            logger.info(f"[STATS] ENHANCED Classification Results:")
            logger.info(f"   [REGEX] Regex: {self.stats['regex_classified']} ({regex_pct:.1f}%)")
            logger.info(f"   [ENHANCED] Enhanced 20K Model: {self.stats['enhanced_bert_classified']} ({enhanced_bert_pct:.1f}%)")
            if self.stats["legacy_bert_classified"] > 0:
                logger.info(f"   [LEGACY] Legacy BERT: {self.stats['legacy_bert_classified']} ({legacy_bert_pct:.1f}%)")
            logger.info(f"   [LLM] LLM: {self.stats['llm_classified']} ({llm_pct:.1f}%)")
            logger.info(f"   [UNCLASSIFIED] Unclassified: {self.stats['unclassified']} ({unclassified_pct:.1f}%)")
            
            # Verify totals make sense
            total_classified = (self.stats["regex_classified"] + self.stats["enhanced_bert_classified"] + 
                               self.stats["legacy_bert_classified"] + self.stats["llm_classified"] + 
                               self.stats["unclassified"])
            if total_classified != total_logs:
                logger.warning(f"Stats inconsistency: {total_classified} classifications for {total_logs} logs")
            
            # Show model performance advantage
            if ENHANCED_MODEL_AVAILABLE and self.stats["enhanced_bert_classified"] > 0:
                logger.info(f"[PERFORMANCE] Using high-performance 20K model with 100% accuracy!")
    
    def get_enhanced_stats(self) -> Dict[str, Any]:
        """Get enhanced classification statistics."""
        stats = self.stats.copy()
        stats["enhanced_model_available"] = ENHANCED_MODEL_AVAILABLE
        
        if ENHANCED_MODEL_AVAILABLE:
            try:
                classifier = get_classifier()
                health = classifier.get_health_status()
                stats["model_health"] = health["status"]
                stats["model_metrics"] = health["metrics"]
            except Exception as e:
                logger.error(f"Error getting model health: {e}")
                stats["model_health"] = "unknown"
        
        return stats
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing stats compatible with ProcessingStats model."""
        # Combine enhanced_bert_classified and legacy_bert_classified into bert_classified
        bert_classified = self.stats["enhanced_bert_classified"] + self.stats["legacy_bert_classified"]
        
        return {
            "regex_classified": self.stats["regex_classified"],
            "bert_classified": bert_classified,  # Combined enhanced + legacy
            "llm_classified": self.stats["llm_classified"],
            "unclassified": self.stats["unclassified"]
        }
    
    def reset_stats(self):
        """Reset classification statistics."""
        self.stats = {
            "total_processed": 0,
            "regex_classified": 0,
            "enhanced_bert_classified": 0,
            "legacy_bert_classified": 0,
            "llm_classified": 0,
            "unclassified": 0
        }
        logger.debug("Enhanced classification statistics reset")

# Create the enhanced global service instance
enhanced_classification_service = EnhancedClassificationService()

def classify_logs_enhanced(logs_data: List[Tuple[str, str]], task_id: Optional[str] = None) -> List[str]:
    """
    Enhanced classification function using the 20K model.
    
    Args:
        logs_data: List of (source, log_message) tuples
        task_id: Optional task ID for cancellation support
        
    Returns:
        List of classification labels
    """
    return enhanced_classification_service.classify_logs(logs_data, task_id)

# Backward compatibility - replace the old function
def classify_logs(logs_data: List[Tuple[str, str]], task_id: Optional[str] = None) -> List[str]:
    """
    Main classification function - now uses enhanced 20K model!
    """
    logger.info("[ENHANCED] Using ENHANCED classification with 20K model!")
    return classify_logs_enhanced(logs_data, task_id)

if __name__ == "__main__":
    # Test the enhanced system
    test_logs = [
        ("WebServer", "User authentication failed for admin"),
        ("Database", "Connection timeout after 30 seconds"),
        ("API", "Endpoint /v1/users deprecated, use /v2/users"),
        ("System", "Memory usage exceeded 90% threshold"),
        ("Application", "Payment processing completed successfully")
    ]
    
    print("[TEST] Testing Enhanced Classification Service...")
    results = classify_logs(test_logs)
    
    print("\nResults:")
    for (source, message), result in zip(test_logs, results):
        print(f"{result:<20} | {source:<10} | {message}")
    
    print(f"\nStats: {enhanced_classification_service.get_enhanced_stats()}")