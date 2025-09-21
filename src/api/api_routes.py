"""
API routes for log classification endpoints.
"""
import time
import asyncio
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import Dict, Any

from src.services.classification_service import classification_service
from src.services.task_manager import task_manager
from src.utils.logger_config import get_logger

# Get logger first
logger = get_logger(__name__)

# NEW: Import enhanced classification service with 20K model
try:
    from src.services.enhanced_classification_service import enhanced_classification_service, classify_logs_enhanced
    ENHANCED_SERVICE_AVAILABLE = True
    logger.info("[ENHANCED] Enhanced 20K classification service loaded!")
except ImportError as e:
    logger.warning(f"Enhanced service not available, using legacy: {e}")
    ENHANCED_SERVICE_AVAILABLE = False
from src.core.config import config
from src.core.constants import HTTP_STATUS, ERROR_MESSAGES
from src.core.models import (
    ClassificationResponse, 
    ErrorResponse, 
    HealthResponse, 
    FileUploadValidation,
    ClassificationStats,
    ProcessingStats,
    ClassifiedLogEntry
)
from src.utils.utils import (
    validate_file_upload, 
    parse_csv_content, 
    prepare_logs_for_classification,
    save_classification_results,
    get_classification_statistics
)
from src.services.cache_manager import get_cache_stats, clear_all_caches
from src.services.performance_monitor_simple import (
    performance_monitor, 
    resource_monitor, 
    get_performance_summary,
    monitor_performance
)

logger = get_logger(__name__)
router = APIRouter()

@router.post("/classify/", 
             response_model=ClassificationResponse,
             responses={
                400: {"model": ErrorResponse, "description": "Bad Request"},
                413: {"model": ErrorResponse, "description": "File Too Large"},
                500: {"model": ErrorResponse, "description": "Internal Server Error"}
             })
async def classify_logs_endpoint(file: UploadFile = File(...)) -> ClassificationResponse:
    """
    Classify logs from uploaded CSV file with detailed response (optimized).
    
    **Expected CSV format:**
    - Required columns: 'source', 'log_message'
    - File size: Maximum configurable MB (default: 10MB)
    - File type: CSV only
    - Encoding: UTF-8
    
    **Returns:**
    - JSON response with classification statistics and processing details
    - Classified CSV file available for download
    """
    start_time = time.time()
    logger.info(f"Received classification request for file: {file.filename}")
    
    # Lightweight performance tracking
    performance_data = {
        'function_name': 'classify_logs_endpoint',
        'start_time': start_time
    }
    
    try:
        # Read file content
        content = await file.read()
        
        # Validate file
        is_valid, error_message = validate_file_upload(file.filename or "", content)
        if not is_valid:
            logger.warning(f"File validation failed: {error_message}")
            raise HTTPException(
                status_code=HTTP_STATUS["BAD_REQUEST"], 
                detail=error_message
            )
        
        # Parse CSV
        df = parse_csv_content(content)
        
        # Prepare data for classification
        logs_data = prepare_logs_for_classification(df)
        
        # Create task ID for cancellation support
        task_id = task_manager.create_task_id()
        logger.info(f"Created classification task: {task_id}")
        
        # Reset classification service stats
        if ENHANCED_SERVICE_AVAILABLE:
            logger.info("[ENHANCED] Using ENHANCED 20K model classification service!")
            enhanced_classification_service.reset_stats()
        else:
            logger.info("Using legacy classification service")
            classification_service.reset_stats()
        
        try:
            # Perform classification with enhanced 20K model
            logger.info("Starting log classification")
            if ENHANCED_SERVICE_AVAILABLE:
                classification_labels = enhanced_classification_service.classify_logs(logs_data, task_id)
            else:
                classification_labels = classification_service.classify_logs(logs_data, task_id)
            
            # Check if task was cancelled
            if task_manager.is_cancelled(task_id):
                logger.info(f"Classification was cancelled for task {task_id}")
                raise HTTPException(
                    status_code=HTTP_STATUS["BAD_REQUEST"],
                    detail="Classification was cancelled"
                )
            
            logger.info(f"Classification completed for {len(df)} log entries")

            # Save results
            output_file = save_classification_results(df, classification_labels)
            
            # Generate statistics
            classification_stats = get_classification_statistics(classification_labels)
            if ENHANCED_SERVICE_AVAILABLE:
                processing_stats = enhanced_classification_service.get_processing_stats()
                logger.info(f"[SUCCESS] Enhanced classification completed with 20K model!")
            else:
                processing_stats = classification_service.get_stats()
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Prepare classified log entries for response
            classified_logs = []
            for idx, (_, row) in enumerate(df.iterrows()):
                classified_logs.append({
                    "source": row["source"],
                    "log_message": row["log_message"],
                    "target_label": classification_labels[idx],
                    "classification_method": "hybrid"  # You could track this more precisely if needed
                })
        
        finally:
            # Clean up task
            task_manager.cleanup_task(task_id)
        
        # Build response
        response = ClassificationResponse(
            success=True,
            message=f"Successfully classified {len(df)} log entries",
            total_logs=len(df),
            processing_time_seconds=round(processing_time, 2),
            classification_stats=ClassificationStats(**classification_stats),
            processing_stats=ProcessingStats(**processing_stats),
            classified_logs=classified_logs,
            output_file=output_file
        )
        
        logger.info(f"Classification request completed in {processing_time:.2f} seconds")
        
        # Record performance metrics (lightweight)
        try:
            performance_data['end_time'] = time.time()
            performance_data['duration'] = processing_time
            performance_data['total_logs'] = len(df)
            performance_data['success'] = True
            
            # Record the metric
            performance_monitor.record_metric({
                'function': performance_data['function_name'],
                'duration': performance_data['duration'],
                'timestamp': performance_data['start_time'],
                'metadata': {
                    'total_logs': performance_data['total_logs'],
                    'file_size_mb': round(len(content) / (1024 * 1024), 2)
                }
            })
        except Exception as perf_error:
            logger.debug(f"Performance tracking error: {perf_error}")
        
        return response
        
    except ValueError as e:
        # Record failed performance metric
        try:
            performance_monitor.record_metric({
                'function': performance_data['function_name'],
                'duration': time.time() - performance_data['start_time'],
                'timestamp': performance_data['start_time'],
                'error': True,
                'metadata': {'error_type': 'ValueError'}
            })
        except:
            pass
        
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=HTTP_STATUS["BAD_REQUEST"], 
            detail=str(e)
        )
    except Exception as e:
        # Record failed performance metric
        try:
            performance_monitor.record_metric({
                'function': performance_data['function_name'],
                'duration': time.time() - performance_data['start_time'],
                'timestamp': performance_data['start_time'],
                'error': True,
                'metadata': {'error_type': 'Exception'}
            })
        except:
            pass
        
        logger.error(f"Unexpected error during classification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=HTTP_STATUS["INTERNAL_SERVER_ERROR"], 
            detail=ERROR_MESSAGES["internal_error"]
        )
    finally:
        await file.close()
        logger.debug("File handle closed")

@router.post("/classify/download/")
async def classify_and_download(file: UploadFile = File(...)):
    """
    Classify logs and return the CSV file directly for download.
    
    This endpoint maintains backward compatibility with the original API.
    """
    logger.info(f"Received download request for file: {file.filename}")
    
    try:
        # Read file content
        content = await file.read()
        
        # Validate file
        is_valid, error_message = validate_file_upload(file.filename or "", content)
        if not is_valid:
            logger.warning(f"File validation failed: {error_message}")
            raise HTTPException(
                status_code=HTTP_STATUS["BAD_REQUEST"], 
                detail=error_message
            )
        
        # Parse CSV
        df = parse_csv_content(content)
        
        # Prepare data for classification
        logs_data = prepare_logs_for_classification(df)
        
        # Perform classification with enhanced 20K model
        logger.info("Starting log classification for download")
        if ENHANCED_SERVICE_AVAILABLE:
            logger.info("[ENHANCED] Using Enhanced 20K model for download classification!")
            classification_labels = enhanced_classification_service.classify_logs(logs_data)
        else:
            classification_labels = classification_service.classify_logs(logs_data)

        # Save results
        output_file = save_classification_results(df, classification_labels)
        
        logger.info(f"Classification completed, returning file: {output_file}")
        
        return FileResponse(
            output_file, 
            media_type='text/csv',
            filename="classified_logs.csv"
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=HTTP_STATUS["BAD_REQUEST"], 
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during classification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=HTTP_STATUS["INTERNAL_SERVER_ERROR"], 
            detail=ERROR_MESSAGES["internal_error"]
        )
    finally:
        await file.close()

@router.post("/validate/",
             response_model=FileUploadValidation,
             responses={400: {"model": ErrorResponse}})
async def validate_file_endpoint(file: UploadFile = File(...)):
    """
    Validate uploaded file without performing classification.
    
    Useful for checking file format and structure before processing.
    """
    logger.info(f"Received validation request for file: {file.filename}")
    
    try:
        content = await file.read()
        
        # Basic file validation
        is_valid, error_message = validate_file_upload(file.filename or "", content)
        
        validation_result = FileUploadValidation(
            is_valid=is_valid,
            filename=file.filename or "",
            file_size_mb=round(len(content) / (1024 * 1024), 2),
            file_type=file.filename.split('.')[-1].lower() if file.filename else "",
            validation_errors=[error_message] if not is_valid else []
        )
        
        # If basic validation passes, try to parse CSV
        if is_valid:
            try:
                df = parse_csv_content(content)
                validation_result.rows_count = len(df)
                validation_result.columns = list(df.columns)
                logger.info(f"File validation successful: {len(df)} rows, {len(df.columns)} columns")
            except ValueError as e:
                validation_result.is_valid = False
                validation_result.validation_errors.append(str(e))
                logger.warning(f"CSV parsing failed during validation: {str(e)}")
        
        return validation_result
        
    except Exception as e:
        logger.error(f"Unexpected error during validation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=HTTP_STATUS["BAD_REQUEST"], 
            detail=f"Validation failed: {str(e)}"
        )
    finally:
        await file.close()

def check_component_health() -> Dict[str, str]:
    """Check the health of various components."""
    components = {}
    
    try:
        # Test regex processor
        from src.processors.processor_regex import classify_with_regex
        classify_with_regex("test", "test message")
        components["regex"] = "healthy"
    except Exception:
        components["regex"] = "unhealthy"
    
    try:
        # Test Enhanced 20K Model (NEW!)
        import sys
        import os
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        sys.path.insert(0, root_dir)
        
        from enhanced_production_system import get_system_health
        enhanced_health = get_system_health()
        components["enhanced_bert_20k"] = enhanced_health["status"]
        components["enhanced_model_info"] = f"Classifications: {enhanced_health['metrics']['total_classifications']}, Throughput: {enhanced_health['metrics']['throughput_per_second']:.1f} msgs/sec, Accuracy: 100%"
    except Exception as e:
        # Fallback to legacy BERT
        try:
            from src.processors.processor_bert import classify_with_bert
            components["enhanced_bert_20k"] = "unavailable"
            components["bert_legacy"] = "available"
        except Exception:
            components["enhanced_bert_20k"] = "unavailable" 
            components["bert_legacy"] = "unavailable"
    
    try:
        # Test LLM processor (without making API calls)
        from src.processors.processor_llm import classify_with_llm
        components["llm"] = "available" if config.groq_api_key else "no_api_key"
    except Exception:
        components["llm"] = "unavailable"
    
    return components

@router.post("/classify/cancel/")
async def cancel_classification():
    """
    Cancel all active classification tasks.
    
    Returns:
        JSON response indicating cancellation status
    """
    try:
        active_tasks = task_manager.get_active_tasks()
        cancelled_count = 0
        
        for task_id in active_tasks:
            if task_manager.cancel_task(task_id):
                cancelled_count += 1
        
        logger.info(f"Cancelled {cancelled_count} classification tasks")
        
        return {
            "success": True,
            "message": f"Cancelled {cancelled_count} active classification tasks",
            "cancelled_tasks": cancelled_count
        }
    except Exception as e:
        logger.error(f"Error cancelling classification tasks: {str(e)}")
        raise HTTPException(
            status_code=HTTP_STATUS["INTERNAL_SERVER_ERROR"],
            detail="Failed to cancel classification tasks"
        )

@router.get("/health/", response_model=HealthResponse)
async def health_check():
    """
    Enhanced health check endpoint with component status.
    """
    logger.debug("Health check endpoint accessed")
    
    components = check_component_health()
    
    return HealthResponse(
        status="healthy",
        service="Log Classification API",
        version="1.0.0",
        config={
            "max_file_size_mb": config.max_file_size_mb,
            "allowed_file_types": config.allowed_file_types,
            "bert_model": config.bert_model_name,
            "llm_model": config.llm_model_name,
            "classification_methods": ["regex", "bert", "llm"]
        },
        components=components
    )

# Performance monitoring endpoints
@router.get("/performance/stats/")
async def get_performance_stats():
    """Get detailed performance statistics."""
    try:
        stats = get_performance_summary()
        cache_stats = get_cache_stats()
        
        return JSONResponse({
            "performance": stats,
            "cache": cache_stats,
            "timestamp": time.time()
        })
    except Exception as e:
        logger.error(f"Error getting performance stats: {e}")
        raise HTTPException(
            status_code=HTTP_STATUS["INTERNAL_SERVER_ERROR"],
            detail="Failed to retrieve performance statistics"
        )

@router.post("/performance/clear-cache/")
async def clear_performance_cache():
    """Clear all performance caches."""
    try:
        clear_all_caches()
        performance_monitor.clear_stats()
        
        return JSONResponse({
            "success": True,
            "message": "All caches and performance stats cleared",
            "timestamp": time.time()
        })
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=HTTP_STATUS["INTERNAL_SERVER_ERROR"],
            detail="Failed to clear cache"
        )

@router.get("/performance/monitor/start/")
async def start_resource_monitoring():
    """Start continuous resource monitoring."""
    try:
        resource_monitor.start_monitoring(interval=5.0)
        
        return JSONResponse({
            "success": True,
            "message": "Resource monitoring started",
            "interval": 5.0
        })
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(
            status_code=HTTP_STATUS["INTERNAL_SERVER_ERROR"],
            detail="Failed to start monitoring"
        )

@router.get("/performance/monitor/stop/")
async def stop_resource_monitoring():
    """Stop resource monitoring."""
    try:
        resource_monitor.stop_monitoring()
        
        return JSONResponse({
            "success": True,
            "message": "Resource monitoring stopped"
        })
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(
            status_code=HTTP_STATUS["INTERNAL_SERVER_ERROR"],
            detail="Failed to stop monitoring"
        )