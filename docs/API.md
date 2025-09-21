# API Documentation

## Overview
The Log Classification API provides endpoints for classifying log messages using a hybrid approach combining regex patterns, BERT embeddings, and LLM analysis.

## Architecture

### Classification Flow
1. **Regex Classification**: Fast pattern matching for common log types
2. **BERT Classification**: ML-based classification using sentence embeddings
3. **LLM Classification**: Advanced analysis using Large Language Models (Groq)

### Components
- `server.py`: FastAPI web server with classification endpoints
- `classification_service.py`: Orchestrates classification methods
- `processor_regex.py`: Pattern-based classification
- `processor_bert.py`: BERT + Logistic Regression classification
- `processor_llm.py`: Groq LLM integration
- `utils.py`: Common utility functions
- `config.py`: Centralized configuration management
- `constants.py`: Application constants and patterns

## API Endpoints

### POST /classify/
Classify logs from an uploaded CSV file.

**Request:**
- Content-Type: `multipart/form-data`
- File: CSV file with columns `source` and `log_message`
- Max file size: Configurable (default 10MB)

**Response:**
- Content-Type: `text/csv`
- File: Classified logs with added `target_label` column

**Example CSV Input:**
```csv
source,log_message
WebApp,"User john.doe logged in successfully"
LegacyCRM,"ERROR: Database connection failed"
API,"GET /users/123 returned 404"
```

**Example CSV Output:**
```csv
source,log_message,target_label
WebApp,"User john.doe logged in successfully",user_action
LegacyCRM,"ERROR: Database connection failed",workflow_error
API,"GET /users/123 returned 404",system_notification
```

### GET /health
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "service": "Log Classification API",
  "version": "1.0.0",
  "config": {
    "max_file_size_mb": 10,
    "allowed_file_types": ["csv"],
    "classification_methods": ["regex", "bert", "llm"]
  }
}
```

### GET /
Welcome page with basic API information.

## Configuration

The API uses environment variables for configuration:

### Required
- `GROQ_API_KEY`: API key for Groq LLM service

### Optional
- `MAX_FILE_SIZE_MB`: Maximum upload file size (default: 10)
- `ALLOWED_FILE_TYPES`: Allowed file extensions (default: csv)
- `BERT_MODEL_NAME`: BERT model name (default: all-MiniLM-L6-v2)
- `LLM_MODEL_NAME`: LLM model name (default: deepseek-r1-distill-llama-70b)
- `LLM_TEMPERATURE`: LLM temperature (default: 0.5)
- `BERT_CONFIDENCE_THRESHOLD`: BERT confidence threshold (default: 0.5)
- `OUTPUT_DIR`: Output directory (default: resources)

## Classification Categories

The system classifies logs into these categories:
- **user_action**: User interactions and activities
- **system_notification**: System status and informational messages
- **workflow_error**: Errors in business processes
- **deprecation_warning**: Deprecated feature usage warnings
- **unclassified**: Logs that couldn't be classified

## Error Handling

The API provides detailed error responses:
- `400 Bad Request`: Invalid file, missing columns, or malformed CSV
- `413 Request Entity Too Large`: File exceeds size limit
- `500 Internal Server Error`: Unexpected server errors

All errors include descriptive messages and are logged for debugging.

## Performance

### Classification Methods Performance
1. **Regex**: ~1ms per log (fastest)
2. **BERT**: ~10-50ms per log (moderate)
3. **LLM**: ~500-2000ms per log (slowest, highest accuracy)

### Optimization Features
- Lazy loading of ML models to prevent startup delays
- Graceful degradation when models fail to load
- Batch processing for improved throughput
- Comprehensive caching (future enhancement)

## Development

### Running the Server
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Test with sample data
curl -X POST "http://localhost:8000/classify/" \
  -H "accept: text/csv" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.csv"
```

### Logs
Application logs are written to the `logs/` directory with daily rotation.