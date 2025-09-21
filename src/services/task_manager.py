"""
Task cancellation system for log classification requests.
"""
import uuid
from typing import Set
from src.utils.logger_config import get_logger

logger = get_logger(__name__)

class TaskManager:
    """Manages cancellable classification tasks."""
    
    def __init__(self):
        self.cancelled_tasks: Set[str] = set()
        self.active_tasks: Set[str] = set()
        
    def create_task_id(self) -> str:
        """Create a unique task ID."""
        task_id = str(uuid.uuid4())
        self.active_tasks.add(task_id)
        return task_id
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task by ID."""
        if task_id in self.active_tasks:
            self.cancelled_tasks.add(task_id)
            logger.info(f"Cancelled task {task_id}")
            return True
        return False
    
    def is_cancelled(self, task_id: str) -> bool:
        """Check if a task has been cancelled."""
        return task_id in self.cancelled_tasks
    
    def cleanup_task(self, task_id: str):
        """Clean up task resources."""
        self.active_tasks.discard(task_id)
        self.cancelled_tasks.discard(task_id)
        logger.debug(f"Cleaned up task {task_id}")
    
    def get_active_tasks(self) -> Set[str]:
        """Get all active task IDs."""
        return self.active_tasks.copy()

# Global task manager instance
task_manager = TaskManager()