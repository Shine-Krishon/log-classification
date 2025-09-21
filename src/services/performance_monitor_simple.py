"""
Simplified performance monitoring without external dependencies.
"""
import time
import threading
from functools import wraps
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from collections import defaultdict, deque
from src.utils.logger_config import get_logger

logger = get_logger(__name__)

@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    function_name: str
    execution_time: float
    timestamp: float
    args_count: int
    success: bool = True
    error_message: Optional[str] = None

class PerformanceMonitor:
    """Simplified performance monitoring and metrics collection."""
    
    def __init__(self, max_history: int = 1000):
        """Initialize performance monitor."""
        self.max_history = max_history
        self.metrics_history: deque = deque(maxlen=max_history)
        self.function_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'call_count': 0,
            'total_time': 0.0,
            'avg_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'error_count': 0,
            'last_called': None
        })
        self._lock = threading.Lock()
        logger.info(f"Performance monitor initialized with history size: {max_history}")
    
    def record_metric(self, metric: PerformanceMetrics):
        """Record a performance metric."""
        with self._lock:
            self.metrics_history.append(metric)
            
            stats = self.function_stats[metric.function_name]
            stats['call_count'] += 1
            stats['last_called'] = metric.timestamp
            
            if metric.success:
                stats['total_time'] += metric.execution_time
                stats['avg_time'] = stats['total_time'] / stats['call_count']
                stats['min_time'] = min(stats['min_time'], metric.execution_time)
                stats['max_time'] = max(stats['max_time'], metric.execution_time)
            else:
                stats['error_count'] += 1
    
    def get_stats(self, function_name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics."""
        with self._lock:
            if function_name:
                return dict(self.function_stats.get(function_name, {}))
            
            return {
                'total_functions_monitored': len(self.function_stats),
                'total_metrics_recorded': len(self.metrics_history),
                'function_stats': dict(self.function_stats)
            }
    
    def get_recent_metrics(self, limit: int = 100) -> List[PerformanceMetrics]:
        """Get recent performance metrics."""
        with self._lock:
            return list(self.metrics_history)[-limit:]
    
    def get_slow_functions(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        """Get functions that are slower than threshold."""
        with self._lock:
            slow_functions = []
            for func_name, stats in self.function_stats.items():
                if stats['avg_time'] > threshold:
                    slow_functions.append({
                        'function': func_name,
                        'avg_time': stats['avg_time'],
                        'call_count': stats['call_count'],
                        'total_time': stats['total_time']
                    })
            
            return sorted(slow_functions, key=lambda x: x['avg_time'], reverse=True)
    
    def clear_stats(self):
        """Clear all performance statistics."""
        with self._lock:
            self.metrics_history.clear()
            self.function_stats.clear()
            logger.info("Performance statistics cleared")

# Global performance monitor
performance_monitor = PerformanceMonitor()

def monitor_performance(track_memory: bool = False, track_cpu: bool = False):
    """
    Simplified decorator to monitor function performance.
    
    Args:
        track_memory: Ignored in simplified version
        track_cpu: Ignored in simplified version
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            
            error_message = None
            success = True
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_message = str(e)
                raise
            finally:
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Record metrics
                metric = PerformanceMetrics(
                    function_name=func.__name__,
                    execution_time=execution_time,
                    timestamp=end_time,
                    args_count=len(args) + len(kwargs),
                    success=success,
                    error_message=error_message
                )
                
                performance_monitor.record_metric(metric)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            
            error_message = None
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_message = str(e)
                raise
            finally:
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Record metrics
                metric = PerformanceMetrics(
                    function_name=func.__name__,
                    execution_time=execution_time,
                    timestamp=end_time,
                    args_count=len(args) + len(kwargs),
                    success=success,
                    error_message=error_message
                )
                
                performance_monitor.record_metric(metric)
        
        # Check if function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class SimpleResourceMonitor:
    """Simplified resource monitoring without external dependencies."""
    
    def __init__(self):
        """Initialize resource monitor."""
        self.is_monitoring = False
        self.monitor_thread = None
        self.resource_history: deque = deque(maxlen=100)
        self._lock = threading.Lock()
    
    def get_current_usage(self) -> Dict[str, Any]:
        """Get basic system information."""
        return {
            'timestamp': time.time(),
            'monitoring_active': self.is_monitoring,
            'history_size': len(self.resource_history)
        }
    
    def start_monitoring(self, interval: float = 5.0):
        """Start basic monitoring."""
        self.is_monitoring = True
        logger.info("Simple resource monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.is_monitoring = False
        logger.info("Simple resource monitoring stopped")
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get monitoring history."""
        with self._lock:
            return list(self.resource_history)[-limit:]

# Global resource monitor
resource_monitor = SimpleResourceMonitor()

def get_performance_summary() -> Dict[str, Any]:
    """Get simplified performance summary."""
    return {
        'performance_stats': performance_monitor.get_stats(),
        'slow_functions': performance_monitor.get_slow_functions(threshold=0.5),
        'current_resources': resource_monitor.get_current_usage(),
        'monitoring_active': resource_monitor.is_monitoring
    }