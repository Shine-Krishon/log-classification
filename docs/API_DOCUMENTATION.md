# Log Classification API Documentation

## Overview

The Log Classification API is a hybrid system that automatically classifies log messages using three complementary approaches:

1. **Regex-based Classification** (80% efficiency) - Fast pattern matching for common log types
2. **BERT-based Classification** - Machine learning for semantic understanding  
3. **LLM-based Classification** - Advanced AI for complex cases

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Health Check
**GET** `/health`

Returns the system health status and configuration.

**Response:**
```json
{
  "status": "healthy",
  "service": "Log Classification API", 
  "version": "1.0.0",
  "timestamp": "2025-09-13T16:10:22.802647",
  "config": {
    "max_file_size_mb": 10,
    "allowed_file_types": ["csv"],
    "bert_model": "all-MiniLM-L6-v2"
  }
}
```

### File Classification
**POST** `/classify/`

Classify log messages from uploaded CSV file.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file` (required): CSV file with columns `source` and `log_message`
  - `source` (required): Name of the system generating logs

**Example CSV format:**
```csv
source,log_message
UserService,"ERROR: Database connection failed"
AuthService,"INFO: User login successful"
PaymentService,"WARNING: Transaction timeout"
```

**Response:**
```json
{
  "message": "Classification completed successfully",
  "total_logs": 150,
  "processing_time": 2.45,
  "download_url": "/api/v1/download/classified_logs_20250913_161022.csv",
  "statistics": {
    "workflow_error": 45,
    "user_action": 32,
    "system_notification": 28,
    "deprecation_warning": 12,
    "unclassified": 33
  },
  "performance": {
    "regex_classified": 120,
    "bert_classified": 20,
    "llm_classified": 10,
    "avg_processing_time_per_log": 0.016
  }
}
```

### Download Results
**GET** `/download/{filename}`

Download classified results CSV file.

**Response:** CSV file with original data plus `classification` column.

### File Validation
**POST** `/validate/`

Validate CSV file structure without processing.

**Request:** Same as `/classify/` endpoint

**Response:**
```json
{
  "valid": true,
  "message": "File validation successful",
  "details": {
    "total_rows": 150,
    "columns": ["source", "log_message"],
    "file_size_mb": 0.85,
    "estimated_processing_time": 2.4
  }
}
```

### Performance Statistics
**GET** `/performance/stats/`

Get detailed performance metrics and monitoring data.

**Response:**
```json
{
  "performance": {
    "performance_stats": {
      "total_functions_monitored": 3,
      "total_metrics_recorded": 1250,
      "function_stats": {
        "classify_with_regex": {
          "call_count": 1000,
          "total_time": 0.45,
          "avg_time": 0.00045,
          "min_time": 0.0001,
          "max_time": 0.002,
          "error_count": 0
        }
      }
    },
    "slow_functions": [],
    "current_resources": {
      "timestamp": 1757760087.58,
      "monitoring_active": false
    }
  },
  "cache": {
    "memory_cache": {
      "size": 156,
      "max_size": 1000,
      "hit_rate": 0.78,
      "utilization": 15.6
    },
    "file_cache_dir": "cache",
    "file_cache_exists": true
  }
}
```

### Clear Cache
**POST** `/performance/clear-cache/`

Clear all performance caches and reset statistics.

**Response:**
```json
{
  "success": true,
  "message": "All caches and performance stats cleared",
  "timestamp": 1757760107.62
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": "Error category",
  "message": "Human-readable error description",
  "details": "Additional error details (optional)",
  "timestamp": "2025-09-13T16:10:22.802647"
}
```

### Common Error Codes

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | Bad Request | Invalid file format, missing parameters |
| 413 | File Too Large | File exceeds 10MB limit |
| 422 | Validation Error | CSV structure validation failed |
| 500 | Internal Error | Server processing error |

## Classification Categories

The system classifies logs into these categories:

1. **user_action** - User interactions (login, logout, profile changes)
2. **system_notification** - System status updates (startup, backup completion)
3. **workflow_error** - Application errors (database failures, timeouts)
4. **deprecation_warning** - Deprecated feature usage warnings
5. **unclassified** - Logs that don't match any category

## Usage Examples

### Python Client Example

```python
import requests

# Health check
response = requests.get('http://localhost:8000/api/v1/health')
print(response.json())

# File classification
with open('logs.csv', 'rb') as f:
    files = {'file': f}
    data = {'source': 'MyApplication'}
    response = requests.post(
        'http://localhost:8000/api/v1/classify/',
        files=files,
        data=data
    )
    result = response.json()
    print(f"Classified {result['total_logs']} logs")

# Download results
if 'download_url' in result:
    download_response = requests.get(
        f"http://localhost:8000{result['download_url']}"
    )
    with open('classified_results.csv', 'wb') as f:
        f.write(download_response.content)
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/api/v1/health

# File classification
curl -X POST \
  -F "file=@logs.csv" \
  -F "source=MyApp" \
  http://localhost:8000/api/v1/classify/

# Performance stats
curl http://localhost:8000/api/v1/performance/stats/

# Clear cache
curl -X POST http://localhost:8000/api/v1/performance/clear-cache/
```

## Rate Limits and Performance

- **File Size Limit:** 10MB per upload
- **Concurrent Requests:** No hard limit (handled by FastAPI async processing)
- **Processing Speed:** ~60 logs/second average
- **Cache TTL:** 1 hour for classification results
- **Memory Cache:** 1000 entries maximum

## Best Practices

### File Preparation
1. Ensure CSV has `source` and `log_message` columns
2. Use UTF-8 encoding
3. Keep files under 10MB for optimal performance
4. Include meaningful source identifiers

### Performance Optimization
1. Use the same source names for better caching
2. Group similar log types in batches
3. Monitor performance stats regularly
4. Clear cache periodically for fresh results

### Error Handling
1. Always check response status codes
2. Validate files with `/validate/` before processing
3. Handle timeouts for large files
4. Retry failed requests with exponential backoff

## Advanced Features

### Performance Monitoring
The API includes comprehensive performance monitoring:
- Function execution timing
- Cache hit/miss ratios
- System resource usage
- Slow function detection

### Caching Strategy
Multi-level caching for optimal performance:
- **In-memory cache**: Fast access for recent classifications
- **File cache**: Persistent storage across server restarts
- **TTL management**: Automatic cleanup of stale entries

### Hybrid Classification
Intelligent method selection:
1. **Regex first**: Fast pattern matching (80% accuracy)
2. **BERT fallback**: Semantic analysis for complex cases
3. **LLM final**: Advanced reasoning for edge cases

## Support and Troubleshooting

### Common Issues

**File Upload Errors:**
- Check file format (must be CSV)
- Verify file size (under 10MB)
- Ensure UTF-8 encoding

**Classification Issues:**
- Review source/log_message column names
- Check for empty rows or invalid characters
- Monitor performance stats for bottlenecks

**Performance Problems:**
- Clear cache if results seem stale
- Monitor system resources
- Consider breaking large files into smaller batches

### Getting Help

For support and bug reports:
- Email: support@codebasics.io
- Check logs for detailed error messages
- Use `/performance/stats/` to gather diagnostic information