"""
Production-ready log classification system with advanced monitoring and features.
Integrates the 20K model with confidence scoring, monitoring, and robust error handling.
Updated: 2025-09-14 to use 5K dataset model priority
"""
import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
import numpy as np

from processor_bert_enhanced import (
    classify_with_bert, 
    classify_batch, 
    get_model_info,
    load_model
)

@dataclass
class ClassificationResult:
    """Enhanced classification result with metadata."""
    prediction: str
    confidence: float
    processing_time: float
    timestamp: datetime
    model_version: str
    message_length: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result

@dataclass 
class PerformanceMetrics:
    """Performance metrics for monitoring."""
    total_classifications: int = 0
    average_processing_time: float = 0.0
    throughput_per_second: float = 0.0
    error_rate: float = 0.0
    confidence_distribution: Dict[str, int] = None
    category_distribution: Dict[str, int] = None
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.confidence_distribution is None:
            self.confidence_distribution = defaultdict(int)
        if self.category_distribution is None:
            self.category_distribution = defaultdict(int)
        if self.last_updated is None:
            self.last_updated = datetime.now()

class ModelMonitor:
    """Monitor model performance and detect anomalies."""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.recent_results = deque(maxlen=window_size)
        self.metrics = PerformanceMetrics()
        self.anomaly_thresholds = {
            'low_confidence_rate': 0.3,  # Alert if >30% predictions have low confidence
            'error_rate': 0.05,  # Alert if >5% error rate
            'processing_time': 5.0,  # Alert if avg processing time >5 seconds
        }
        self.alerts = []
        self._lock = threading.Lock()
    
    def record_result(self, result: ClassificationResult, error: bool = False):
        """Record a classification result for monitoring."""
        with self._lock:
            self.recent_results.append((result, error))
            self._update_metrics()
            self._check_anomalies()
    
    def _update_metrics(self):
        """Update performance metrics based on recent results."""
        if not self.recent_results:
            return
        
        # Calculate metrics from recent results
        total_count = len(self.recent_results)
        error_count = sum(1 for _, error in self.recent_results if error)
        
        valid_results = [result for result, error in self.recent_results if not error]
        
        if valid_results:
            avg_time = np.mean([r.processing_time for r in valid_results])
            
            # Calculate throughput (results per second over last minute)
            recent_minute = datetime.now() - timedelta(minutes=1)
            recent_count = sum(1 for r, _ in self.recent_results 
                             if r and r.timestamp > recent_minute)
            throughput = recent_count / 60.0
            
            # Confidence distribution
            conf_dist = defaultdict(int)
            for result in valid_results:
                if result.confidence >= 0.8:
                    conf_dist['high'] += 1
                elif result.confidence >= 0.6:
                    conf_dist['medium'] += 1
                else:
                    conf_dist['low'] += 1
            
            # Category distribution
            cat_dist = defaultdict(int)
            for result in valid_results:
                cat_dist[result.prediction] += 1
            
            self.metrics = PerformanceMetrics(
                total_classifications=total_count,
                average_processing_time=avg_time,
                throughput_per_second=throughput,
                error_rate=error_count / total_count if total_count > 0 else 0.0,
                confidence_distribution=dict(conf_dist),
                category_distribution=dict(cat_dist),
                last_updated=datetime.now()
            )
    
    def _check_anomalies(self):
        """Check for anomalies and generate alerts."""
        current_time = datetime.now()
        
        # Check low confidence rate
        total_conf = sum(self.metrics.confidence_distribution.values())
        if total_conf > 0:
            low_conf_rate = self.metrics.confidence_distribution.get('low', 0) / total_conf
            if low_conf_rate > self.anomaly_thresholds['low_confidence_rate']:
                self.alerts.append({
                    'type': 'LOW_CONFIDENCE_RATE',
                    'message': f'High rate of low-confidence predictions: {low_conf_rate:.2%}',
                    'timestamp': current_time,
                    'severity': 'WARNING'
                })
        
        # Check error rate
        if self.metrics.error_rate > self.anomaly_thresholds['error_rate']:
            self.alerts.append({
                'type': 'HIGH_ERROR_RATE',
                'message': f'High error rate detected: {self.metrics.error_rate:.2%}',
                'timestamp': current_time,
                'severity': 'ERROR'
            })
        
        # Check processing time
        if self.metrics.average_processing_time > self.anomaly_thresholds['processing_time']:
            self.alerts.append({
                'type': 'SLOW_PROCESSING',
                'message': f'Slow processing detected: {self.metrics.average_processing_time:.2f}s avg',
                'timestamp': current_time,
                'severity': 'WARNING'
            })
        
        # Keep only recent alerts (last hour)
        cutoff_time = current_time - timedelta(hours=1)
        self.alerts = [alert for alert in self.alerts if alert['timestamp'] > cutoff_time]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status and metrics."""
        with self._lock:
            return {
                'status': 'healthy' if not any(a['severity'] == 'ERROR' for a in self.alerts) else 'unhealthy',
                'metrics': asdict(self.metrics),
                'alerts': self.alerts[-10:],  # Last 10 alerts
                'model_info': get_model_info(),
                'timestamp': datetime.now().isoformat()
            }

class EnhancedLogClassifier:
    """Production-ready log classifier with monitoring and advanced features."""
    
    def __init__(self):
        self.monitor = ModelMonitor()
        self.model_info = None
        self.logger = self._setup_logging()
        
        # Load model and get info
        if load_model():
            self.model_info = get_model_info()
            self.logger.info(f"Enhanced classifier initialized with model: {self.model_info.get('model_path')}")
        else:
            self.logger.error("Failed to load classification model")
            raise RuntimeError("Model loading failed")
    
    def _setup_logging(self) -> logging.Logger:
        """Set up dedicated logger for the classifier."""
        logger = logging.getLogger('enhanced_classifier')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def classify_single(self, message: str, include_metadata: bool = True) -> Dict[str, Any]:
        """
        Classify a single log message with enhanced features.
        
        Args:
            message: Log message to classify
            include_metadata: Whether to include detailed metadata
            
        Returns:
            Dictionary with classification result and metadata
        """
        start_time = time.time()
        
        try:
            # Perform classification
            prediction = classify_with_bert(message)
            processing_time = time.time() - start_time
            
            # Calculate confidence (if model supports it)
            confidence = self._calculate_confidence(message, prediction)
            
            # Create result object
            result = ClassificationResult(
                prediction=prediction,
                confidence=confidence,
                processing_time=processing_time,
                timestamp=datetime.now(),
                model_version=self.model_info.get('model_path', 'unknown'),
                message_length=len(message)
            )
            
            # Record for monitoring
            self.monitor.record_result(result, error=False)
            
            self.logger.debug(f"Classified message: {prediction} (confidence: {confidence:.3f})")
            
            if include_metadata:
                return {
                    'prediction': prediction,
                    'confidence': confidence,
                    'processing_time': processing_time,
                    'metadata': {
                        'message_length': len(message),
                        'model_version': result.model_version,
                        'timestamp': result.timestamp.isoformat()
                    }
                }
            else:
                return {'prediction': prediction}
                
        except Exception as e:
            processing_time = time.time() - start_time
            error_result = ClassificationResult(
                prediction='unclassified',
                confidence=0.0,
                processing_time=processing_time,
                timestamp=datetime.now(),
                model_version=self.model_info.get('model_path', 'unknown'),
                message_length=len(message) if message else 0
            )
            
            self.monitor.record_result(error_result, error=True)
            self.logger.error(f"Classification error: {str(e)}", exc_info=True)
            
            return {
                'prediction': 'unclassified',
                'confidence': 0.0,
                'error': str(e),
                'processing_time': processing_time
            }
    
    def classify_batch(self, messages: List[str], include_metadata: bool = True) -> List[Dict[str, Any]]:
        """
        Classify multiple messages efficiently.
        
        Args:
            messages: List of log messages to classify
            include_metadata: Whether to include detailed metadata
            
        Returns:
            List of classification results
        """
        if not messages:
            return []
        
        start_time = time.time()
        
        try:
            # Batch classification for efficiency
            predictions = classify_batch(messages)
            total_processing_time = time.time() - start_time
            avg_processing_time = total_processing_time / len(messages)
            
            results = []
            for i, (message, prediction) in enumerate(zip(messages, predictions)):
                confidence = self._calculate_confidence(message, prediction)
                
                result = ClassificationResult(
                    prediction=prediction,
                    confidence=confidence,
                    processing_time=avg_processing_time,
                    timestamp=datetime.now(),
                    model_version=self.model_info.get('model_path', 'unknown'),
                    message_length=len(message)
                )
                
                self.monitor.record_result(result, error=False)
                
                if include_metadata:
                    result_dict = result.to_dict()
                else:
                    result_dict = {'prediction': prediction}
                
                results.append(result_dict)
            
            self.logger.info(f"Batch classified {len(messages)} messages in {total_processing_time:.3f}s")
            return results
            
        except Exception as e:
            self.logger.error(f"Batch classification error: {str(e)}", exc_info=True)
            
            # Return error results for all messages
            error_results = []
            for message in messages:
                error_result = {
                    'prediction': 'unclassified',
                    'confidence': 0.0,
                    'error': str(e)
                }
                if include_metadata:
                    error_result['metadata'] = {
                        'message_length': len(message),
                        'timestamp': datetime.now().isoformat()
                    }
                error_results.append(error_result)
            
            return error_results
    
    def _calculate_confidence(self, message: str, prediction: str) -> float:
        """
        Calculate confidence score for a prediction.
        This is a simplified implementation - could be enhanced with actual model confidence.
        """
        # Simple heuristic based on message characteristics and prediction
        if prediction == 'unclassified':
            return 0.1
        
        # Higher confidence for longer, more structured messages
        length_factor = min(len(message) / 100.0, 1.0)
        
        # Higher confidence for messages with common log patterns
        pattern_factor = 0.5
        log_patterns = ['error', 'warning', 'info', 'debug', 'failed', 'success', 'timeout', 'connection']
        for pattern in log_patterns:
            if pattern.lower() in message.lower():
                pattern_factor = 0.8
                break
        
        base_confidence = 0.6 + (length_factor * 0.2) + (pattern_factor * 0.2)
        return min(base_confidence, 1.0)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and metadata."""
        return self.model_info if self.model_info else {}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        return self.monitor.get_health_status()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics."""
        return asdict(self.monitor.metrics)
    
    def reset_metrics(self):
        """Reset performance metrics (useful for testing)."""
        self.monitor = ModelMonitor()
        self.logger.info("Performance metrics reset")

# Global classifier instance for use across the application
_classifier_instance = None
_classifier_lock = threading.Lock()

def get_classifier() -> EnhancedLogClassifier:
    """Get or create the global classifier instance (singleton pattern)."""
    global _classifier_instance
    
    with _classifier_lock:
        if _classifier_instance is None:
            _classifier_instance = EnhancedLogClassifier()
        return _classifier_instance

def reset_classifier():
    """Reset the global classifier instance to force reinitialization with new model."""
    global _classifier_instance
    
    with _classifier_lock:
        _classifier_instance = None

# Convenience functions for easy integration
def classify_log_message(message: str, include_metadata: bool = False) -> Dict[str, Any]:
    """Convenience function to classify a single log message."""
    classifier = get_classifier()
    return classifier.classify_single(message, include_metadata)

def classify_log_messages(messages: List[str], include_metadata: bool = False) -> List[Dict[str, Any]]:
    """Convenience function to classify multiple log messages."""
    classifier = get_classifier()
    return classifier.classify_batch(messages, include_metadata)

def get_system_health() -> Dict[str, Any]:
    """Convenience function to get system health status."""
    classifier = get_classifier()
    return classifier.get_health_status()

if __name__ == "__main__":
    # Demo the enhanced system
    print("=== Enhanced Log Classification System Demo ===")
    
    classifier = EnhancedLogClassifier()
    
    # Test single message
    test_message = "User authentication failed for admin user"
    result = classifier.classify_single(test_message, include_metadata=True)
    print(f"\nSingle message classification:")
    print(json.dumps(result, indent=2))
    
    # Test batch messages
    test_messages = [
        "Database connection timeout after 30 seconds",
        "API endpoint /v1/users deprecated, use /v2/users",
        "Memory usage exceeded 90% threshold",
        "File upload completed successfully",
        "Unknown error in payment processing"
    ]
    
    batch_results = classifier.classify_batch(test_messages, include_metadata=True)
    print(f"\nBatch classification results:")
    for i, result in enumerate(batch_results):
        print(f"{i+1}. {result['prediction']} (conf: {result['confidence']:.3f}) - {test_messages[i]}")
    
    # Show health status
    health = classifier.get_health_status()
    print(f"\nSystem health status:")
    print(f"Status: {health['status']}")
    print(f"Total classifications: {health['metrics']['total_classifications']}")
    print(f"Average processing time: {health['metrics']['average_processing_time']:.3f}s")
    print(f"Throughput: {health['metrics']['throughput_per_second']:.1f} msgs/sec")
    
    if health['alerts']:
        print(f"Active alerts: {len(health['alerts'])}")
        for alert in health['alerts'][-3:]:  # Show last 3 alerts
            print(f"  - {alert['type']}: {alert['message']}")
    else:
        print("No active alerts")