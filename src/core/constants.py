"""
Constants for the log classification project.
"""
from typing import Dict

# Regex patterns for log classification
REGEX_PATTERNS: Dict[str, str] = {
    # User Actions (legitimate user activities) - SECURITY REMOVED to let enhanced model handle
    r"user.*log(ged|s)?\s*(in|out).*success": "user_action",  # Only successful logins
    r"login.*success|logout|authentication.*success|sign.*in.*success": "user_action",
    r"user.*created|registered|account.*created": "user_action",
    r"password.*changed|updated.*profile|profile.*updated": "user_action",
    r"file.*uploaded.*by.*user|document.*created.*by": "user_action",
    
    # System Notifications (general system events) - SECURITY REMOVED
    r"backup.*completed|successfully.*backup": "system_notification",
    r"(?:^|\s)system.*updated?|version.*updated?": "system_notification",
    r"(?:get|post|put|delete)(?!.*(?:fail|error|timeout)).*\d{3}": "system_notification",
    r"connection.*established|server.*started": "system_notification",
    r"(?:scheduled.*task|cron.*job)(?!.*(?:user|fail|error|abort|request))": "system_notification",
    r"application.*start|service.*start|(?:listening|bound|running).*port.*\d+": "system_notification",
    
    # Workflow Errors - NON-SECURITY related only
    r"database.*error|sql.*error|query.*failed": "workflow_error",
    r"network.*error|connection.*timeout": "workflow_error",
    r"file.*not.*found": "workflow_error",
    r"process.*abort|operation.*abort": "workflow_error",
    r"workflow.*fail|timeout.*error": "workflow_error",
    
    # Deprecation Warnings
    r"deprecat(ed|ion)|warning.*deprecat": "deprecation_warning",
    r"feature.*removed|legacy.*feature": "deprecation_warning",
    r"obsolete|will.*be.*removed|retire.*in.*version": "deprecation_warning",
    r"no.*longer.*supported|feature.*discontinued": "deprecation_warning"
}

# LLM Classification Prompt Template
LLM_CLASSIFICATION_PROMPT = """Classify the log message into one of these categories: 
(1) Workflow Error, (2) Deprecation Warning.
If you can't figure out a category, use "Unclassified".
Put the category inside <category> </category> tags. 
Log message: {log_message}"""

# HTTP Status Codes
HTTP_STATUS = {
    "OK": 200,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "NOT_FOUND": 404,
    "REQUEST_ENTITY_TOO_LARGE": 413,
    "INTERNAL_SERVER_ERROR": 500
}

# Error Messages
ERROR_MESSAGES = {
    "no_file": "No file provided",
    "invalid_file_type": "File must be one of: {allowed_types}",
    "file_too_large": "File too large. Maximum size: {max_size}MB",
    "missing_columns": "CSV must contain columns: {missing_columns}",
    "empty_csv": "CSV file is empty",
    "invalid_encoding": "File must be UTF-8 encoded",
    "invalid_csv": "Invalid CSV format: {error}",
    "internal_error": "Internal server error during processing"
}

# API Metadata
API_METADATA = {
    "title": "Log Classification API",
    "description": "A hybrid log classification system using regex, BERT, and LLM approaches",
    "version": "1.0.0",
    "contact": {
        "name": "Codebasics Inc",
        "email": "support@codebasics.io"
    }
}

# Classification Method Priority
CLASSIFICATION_METHODS = [
    "regex",
    "bert", 
    "llm"
]