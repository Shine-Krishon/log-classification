"""
Pydantic models for API request and response validation.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime

class ClassificationStats(BaseModel):
    """Statistics about the classification process."""
    total_logs: int = Field(..., description="Total number of logs processed")
    label_counts: Dict[str, int] = Field(..., description="Count of each label")
    label_percentages: Dict[str, float] = Field(..., description="Percentage of each label")
    
class ProcessingStats(BaseModel):
    """Statistics about which processing methods were used."""
    regex_classified: int = Field(..., description="Number of logs classified by regex")
    bert_classified: int = Field(..., description="Number of logs classified by BERT")
    llm_classified: int = Field(..., description="Number of logs classified by LLM")
    unclassified: int = Field(..., description="Number of unclassified logs")

class ClassifiedLogEntry(BaseModel):
    """A single classified log entry."""
    source: str = Field(..., description="Source system of the log")
    log_message: str = Field(..., description="Original log message")
    target_label: str = Field(..., description="Classification result")
    classification_method: Optional[str] = Field(None, description="Method used for classification")

class ClassificationResponse(BaseModel):
    """Response model for classification endpoint."""
    success: bool = Field(..., description="Whether classification was successful")
    message: str = Field(..., description="Status message")
    total_logs: int = Field(..., description="Total number of logs processed")
    processing_time_seconds: float = Field(..., description="Time taken to process")
    classification_stats: ClassificationStats = Field(..., description="Classification statistics")
    processing_stats: ProcessingStats = Field(..., description="Processing method statistics")
    classified_logs: List[ClassifiedLogEntry] = Field(..., description="The actual classified log entries")
    output_file: str = Field(..., description="Path to output file")
    timestamp: datetime = Field(default_factory=datetime.now, description="Processing timestamp")

class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Detailed error message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    config: Dict[str, Any] = Field(..., description="Current configuration")
    components: Dict[str, str] = Field(..., description="Component status")

class FileUploadValidation(BaseModel):
    """File upload validation result."""
    is_valid: bool = Field(..., description="Whether file is valid")
    filename: str = Field(..., description="Original filename")
    file_size_mb: float = Field(..., description="File size in MB")
    file_type: str = Field(..., description="File extension")
    rows_count: Optional[int] = Field(None, description="Number of rows if CSV parsed")
    columns: Optional[List[str]] = Field(None, description="Column names if CSV parsed")
    validation_errors: List[str] = Field(default_factory=list, description="Validation error messages")

class ClassificationRequest(BaseModel):
    """Request model for batch classification (future use)."""
    logs: List[Dict[str, str]] = Field(..., description="List of log entries")
    source_column: str = Field(default="source", description="Name of source column")
    message_column: str = Field(default="log_message", description="Name of message column")
    
    @validator('logs')
    def validate_logs(cls, v):
        if not v:
            raise ValueError("At least one log entry is required")
        return v

class BatchClassificationResponse(BaseModel):
    """Response model for batch classification."""
    success: bool = Field(..., description="Whether classification was successful")
    results: List[Dict[str, Any]] = Field(..., description="Classification results")
    total_processed: int = Field(..., description="Total logs processed")
    processing_time_seconds: float = Field(..., description="Processing time")
    classification_stats: ClassificationStats = Field(..., description="Classification statistics")
    timestamp: datetime = Field(default_factory=datetime.now, description="Processing timestamp")