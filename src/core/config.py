"""
Configuration management for the log classification project.
"""
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

class Config:
    """Application configuration class."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        load_dotenv()
        
        # API Configuration
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        # File Upload Configuration
        self.max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
        self.max_file_size_bytes = self.max_file_size_mb * 1024 * 1024
        self.allowed_file_types = os.getenv("ALLOWED_FILE_TYPES", "csv").split(",")
        
        # Model Configuration
        self.bert_model_name = os.getenv("BERT_MODEL_NAME", "all-MiniLM-L6-v2")
        self.llm_model_name = os.getenv("LLM_MODEL_NAME", "llama-3.1-70b-versatile")
        self.llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0"))
        
        # Classification Configuration
        self.bert_confidence_threshold = float(os.getenv("BERT_CONFIDENCE_THRESHOLD", "0.5"))
        self.model_path = os.getenv("MODEL_PATH", "models/log_classifier.joblib")  # 5K dataset model (100% accuracy)
        self.fallback_model_path = "models/enhanced_log_classifier.joblib"  # Enhanced model as fallback
        
        # Output Configuration
        self.output_dir = os.getenv("OUTPUT_DIR", "resources")
        self.output_filename = os.getenv("OUTPUT_FILENAME", "output.csv")
        
        # CSV Column Configuration
        self.required_columns = ["source", "log_message"]
        self.target_column = "target_label"
        
        # Classification Categories
        self.classification_categories = {
            "user_action": "User Action",
            "system_notification": "System Notification", 
            "workflow_error": "Workflow Error",
            "deprecation_warning": "Deprecation Warning",
            "security_alert": "Security Alert",
            "unclassified": "Unclassified"
        }
        
        # Source-specific Configuration
        self.legacy_sources = ["LegacyCRM"]  # Sources that use LLM classification
        
    def get_output_path(self) -> str:
        """Get the full output file path."""
        os.makedirs(self.output_dir, exist_ok=True)
        return os.path.join(self.output_dir, self.output_filename)
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        errors = []
        
        if self.max_file_size_mb <= 0:
            errors.append("MAX_FILE_SIZE_MB must be positive")
        
        if self.bert_confidence_threshold < 0 or self.bert_confidence_threshold > 1:
            errors.append("BERT_CONFIDENCE_THRESHOLD must be between 0 and 1")
            
        if self.llm_temperature < 0 or self.llm_temperature > 2:
            errors.append("LLM_TEMPERATURE must be between 0 and 2")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for logging."""
        return {
            "max_file_size_mb": self.max_file_size_mb,
            "allowed_file_types": self.allowed_file_types,
            "bert_model_name": self.bert_model_name,
            "llm_model_name": self.llm_model_name,
            "llm_temperature": self.llm_temperature,
            "bert_confidence_threshold": self.bert_confidence_threshold,
            "output_dir": self.output_dir,
            "legacy_sources": self.legacy_sources
        }

# Global configuration instance
config = Config()
config.validate()