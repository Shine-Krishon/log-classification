"""
Performance monitoring and optimization utilities.
"""
import time
import psutil  # Re-enabled after installing psutil
import threading
from functools import wraps
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from logger_config import get_logger

logger = get_logger(__name__)

@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    function_name: str
    execution_time: float
    memory_before: float = 0.0
    memory_after: float = 0.0
    cpu_percent: float = 0.0
    timestamp: float = 0.0
    args_count: int = 0
    success: bool = True
    error_message: Optional[str] = None

class PerformanceMonitor:
    """Performance monitoring and metrics collection."""
    
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

def monitor_performance(track_memory: bool = True, track_cpu: bool = True):
    """
    Decorator to monitor function performance.
    
    Args:
        track_memory: Whether to track memory usage
        track_cpu: Whether to track CPU usage
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Get initial system metrics
            memory_before = psutil.Process().memory_info().rss / 1024 / 1024 if track_memory else 0  # MB
            cpu_percent = psutil.cpu_percent() if track_cpu else 0
            
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
                
                # Get final memory usage
                memory_after = psutil.Process().memory_info().rss / 1024 / 1024 if track_memory else 0  # MB
                
                # Record metrics
                metric = PerformanceMetrics(
                    function_name=func.__name__,
                    execution_time=execution_time,
                    memory_before=memory_before,
                    memory_after=memory_after,
                    cpu_percent=cpu_percent,
                    timestamp=end_time,
                    args_count=len(args) + len(kwargs),
                    success=success,
                    error_message=error_message
                )
                
                performance_monitor.record_metric(metric)
                
                # Log slow operations
                if execution_time > 2.0:  # More than 2 seconds
                    logger.warning(f"Slow operation detected: {func.__name__} took {execution_time:.2f}s")
        
        return wrapper
    return decorator

class ResourceMonitor:
    """System resource monitoring."""
    
    def __init__(self):
        """Initialize resource monitor."""
        self.is_monitoring = False
        self.monitor_thread = None
        self.resource_history: deque = deque(maxlen=100)
        self._lock = threading.Lock()
    
    def start_monitoring(self, interval: float = 5.0):
        """Start continuous resource monitoring."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info(f"Started resource monitoring with {interval}s interval")
    
    def stop_monitoring(self):
        """Stop resource monitoring."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        logger.info("Stopped resource monitoring")
    
    def _monitor_loop(self, interval: float):
        """Resource monitoring loop."""
        while self.is_monitoring:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                process = psutil.Process()
                process_memory = process.memory_info().rss / 1024 / 1024  # MB
                
                metrics = {
                    'timestamp': time.time(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_mb': memory.available / 1024 / 1024,
                    'process_memory_mb': process_memory,
                    'process_cpu_percent': process.cpu_percent()
                }
                
                with self._lock:
                    self.resource_history.append(metrics)
                
                # Alert on high resource usage
                if cpu_percent > 80:
                    logger.warning(f"High CPU usage detected: {cpu_percent}%")
                if memory.percent > 85:
                    logger.warning(f"High memory usage detected: {memory.percent}%")
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                time.sleep(interval)
    
    def get_current_usage(self) -> Dict[str, Any]:
        """Get current resource usage."""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            process = psutil.Process()
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_total_gb': memory.total / 1024 / 1024 / 1024,
                'memory_available_gb': memory.available / 1024 / 1024 / 1024,
                'process_memory_mb': process.memory_info().rss / 1024 / 1024,
                'process_cpu_percent': process.cpu_percent(),
                'disk_usage': {path: psutil.disk_usage(path).percent for path in ['/', 'C:\\'] if psutil.disk_usage(path)}
            }
        except Exception as e:
            logger.error(f"Error getting resource usage: {e}")
            return {}
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get resource usage history."""
        with self._lock:
            return list(self.resource_history)[-limit:]

# Global resource monitor
resource_monitor = ResourceMonitor()

def get_performance_summary() -> Dict[str, Any]:
    """Get comprehensive performance summary."""
    return {
        'performance_stats': performance_monitor.get_stats(),
        'slow_functions': performance_monitor.get_slow_functions(threshold=0.5),
        'current_resources': resource_monitor.get_current_usage(),
        'resource_history': resource_monitor.get_history(10)
    }