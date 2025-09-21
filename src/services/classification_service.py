"""
Classification service that orchestrates the different classification methods.
"""
from typing import List, Tuple, Dict, Any, Optional
from src.utils.logger_config import get_logger
from src.core.config import config
from src.processors.processor_regex import classify_with_regex
from src.processors.processor_bert import classify_with_bert
from src.processors.processor_llm import classify_with_llm

logger = get_logger(__name__)

class ClassificationService:
    """Service for managing log classification across different methods."""
    
    def __init__(self):
        """Initialize the classification service."""
        self.stats = {
            "total_processed": 0,
            "regex_classified": 0,
            "bert_classified": 0,
            "llm_classified": 0,
            "unclassified": 0
        }
        logger.info("Classification service initialized")
    
    def classify_logs(self, logs_data: List[Tuple[str, str]], task_id: Optional[str] = None) -> List[str]:
        """
        Classify a list of logs using the hybrid approach with batch optimization.
        
        Args:
            logs_data: List of (source, log_message) tuples
            task_id: Optional task ID for cancellation support
            
        Returns:
            List of classification labels
        """
        logger.info(f"Starting classification for {len(logs_data)} log entries (task: {task_id})")
        self.stats["total_processed"] = len(logs_data)
        
        # Phase 1: Process all logs with regex and BERT, collect LLM candidates
        results = ["unclassified"] * len(logs_data)
        llm_candidates = []  # (index, source, log_message)
        
        for i, (source, log_message) in enumerate(logs_data):
            # Check for cancellation
            if task_id:
                from src.services.task_manager import task_manager
                if task_manager.is_cancelled(task_id):
                    logger.info(f"Classification cancelled for task {task_id} at record {i+1}")
                    return ["cancelled"] * len(logs_data)
            
            try:
                # Try regex first
                from src.processors.processor_regex import classify_with_regex
                regex_result = classify_with_regex(source, log_message)
                
                if regex_result != "unclassified":
                    results[i] = regex_result
                    self.stats["regex_classified"] += 1
                    continue
                
                # For legacy sources, queue for LLM
                if source in config.legacy_sources:
                    llm_candidates.append((i, source, log_message))
                    continue
                
                # Try BERT for non-legacy sources
                from src.processors.processor_bert import classify_with_bert
                bert_result = classify_with_bert(source, log_message)
                
                if bert_result != "unclassified":
                    results[i] = bert_result
                    self.stats["bert_classified"] += 1
                else:
                    # Queue for LLM as fallback
                    llm_candidates.append((i, source, log_message))
                    
            except Exception as e:
                logger.error(f"Error classifying log {i+1}: {str(e)}")
                llm_candidates.append((i, source, log_message))  # Try LLM as fallback
        
        # Phase 2: Batch process LLM candidates
        if llm_candidates:
            logger.debug(f"Processing {len(llm_candidates)} logs with LLM in batch")
            
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
                # Fallback to individual processing for LLM candidates
                for index, source, log_message in llm_candidates:
                    try:
                        from src.processors.processor_llm import classify_with_llm
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
        
        # Update remaining unclassified
        unclassified_count = sum(1 for result in results if result == "unclassified")
        self.stats["unclassified"] = unclassified_count
        
        # Log final progress
        logger.info(f"Progress: {len(logs_data)}/{len(logs_data)} logs (100.0%)")
        self._log_classification_stats()
        return results
    
    def _classify_single_log(self, source: str, log_message: str, task_id: str = None) -> str:
        """
        Classify a single log entry using the hybrid approach.
        
        Args:
            source: Log source identifier
            log_message: Log message content
            task_id: Task ID for cancellation support
            
        Returns:
            Classification label
        """
        import time
        start_time = time.time()
        
        # Step 1: Try regex classification
        regex_start = time.time()
        regex_result = classify_with_regex(source, log_message)
        regex_time = time.time() - regex_start
        
        if regex_result != "unclassified":
            self.stats["regex_classified"] += 1
            logger.debug(f"Regex classified: {source} -> {regex_result} (took {regex_time:.3f}s)")
            return regex_result
        
        # Step 2: For legacy sources, use LLM directly
        if source in config.legacy_sources:
            llm_start = time.time()
            llm_result = classify_with_llm(source, log_message, task_id)
            llm_time = time.time() - llm_start
            
            if llm_result != "unclassified":
                self.stats["llm_classified"] += 1
                logger.debug(f"LLM classified: {source} -> {llm_result} (took {llm_time:.3f}s)")
                return llm_result
        else:
            # Step 3: Try BERT classification for modern sources
            bert_start = time.time()
            bert_result = classify_with_bert(source, log_message)
            bert_time = time.time() - bert_start
            
            if bert_result != "unclassified":
                self.stats["bert_classified"] += 1
                logger.debug(f"BERT classified: {source} -> {bert_result} (took {bert_time:.3f}s)")
                return bert_result
            
            # Step 4: Fallback to LLM for complex cases
            llm_start = time.time()
            llm_result = classify_with_llm(source, log_message, task_id)
            llm_time = time.time() - llm_start
            
            if llm_result != "unclassified":
                self.stats["llm_classified"] += 1
                logger.debug(f"LLM fallback classified: {source} -> {llm_result} (took {llm_time:.3f}s)")
                return llm_result
        
        # Final fallback
        total_time = time.time() - start_time
        self.stats["unclassified"] += 1
        logger.warning(f"Unable to classify log from {source}: {log_message[:100]}... (took {total_time:.3f}s)")
        return "unclassified"
    
    def _log_classification_stats(self):
        """Log classification statistics."""
        if self.stats["total_processed"] > 0:
            regex_pct = (self.stats["regex_classified"] / self.stats["total_processed"]) * 100
            bert_pct = (self.stats["bert_classified"] / self.stats["total_processed"]) * 100
            llm_pct = (self.stats["llm_classified"] / self.stats["total_processed"]) * 100
            unclassified_pct = (self.stats["unclassified"] / self.stats["total_processed"]) * 100
            
            logger.info(f"Classification completed: "
                       f"Regex: {self.stats['regex_classified']} ({regex_pct:.1f}%), "
                       f"BERT: {self.stats['bert_classified']} ({bert_pct:.1f}%), "
                       f"LLM: {self.stats['llm_classified']} ({llm_pct:.1f}%), "
                       f"Unclassified: {self.stats['unclassified']} ({unclassified_pct:.1f}%)")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get classification statistics."""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset classification statistics."""
        self.stats = {
            "total_processed": 0,
            "regex_classified": 0,
            "bert_classified": 0,
            "llm_classified": 0,
            "unclassified": 0
        }
        logger.debug("Classification statistics reset")

# Global service instance
classification_service = ClassificationService()

def classify_logs(logs_data: List[Tuple[str, str]], task_id: Optional[str] = None) -> List[str]:
    """
    Main classification function for backward compatibility.
    
    Args:
        logs_data: List of (source, log_message) tuples
        task_id: Optional task ID for cancellation support
        
    Returns:
        List of classification labels
    """
    return classification_service.classify_logs(logs_data, task_id)