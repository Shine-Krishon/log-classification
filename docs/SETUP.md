# Setup and Installation Guide

## Prerequisites
- Python 3.8 or higher
- pip package manager
- Internet connection for downloading models

## Installation

### 1. Clone or Download the Project
```bash
git clone <repository-url>
cd project-nlp-log-classification
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:
```env
# Required: Groq API key for LLM classification
GROQ_API_KEY=your_groq_api_key_here

# Optional configurations
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=csv
BERT_MODEL_NAME=all-MiniLM-L6-v2
LLM_MODEL_NAME=deepseek-r1-distill-llama-70b
LLM_TEMPERATURE=0.5
BERT_CONFIDENCE_THRESHOLD=0.5
OUTPUT_DIR=resources
```

### 5. Get Groq API Key
1. Visit [Groq Console](https://console.groq.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Generate a new API key
5. Add it to your `.env` file

### 6. Test Installation
```bash
python -c "from server import app; print('Installation successful!')"
```

## Running the Application

### Start the Server
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Access the API
- Web interface: http://localhost:8000
- API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Directory Structure
```
project-nlp-log-classification/
├── server.py                 # FastAPI web server
├── classification_service.py # Main classification logic
├── processor_bert.py         # BERT classification
├── processor_llm.py          # LLM classification
├── processor_regex.py        # Regex classification
├── classify.py              # Legacy classification entry point
├── utils.py                 # Utility functions
├── config.py                # Configuration management
├── constants.py             # Application constants
├── logger_config.py         # Logging configuration
├── requirements.txt         # Python dependencies
├── README.md               # Project overview
├── .env                    # Environment variables (create this)
├── models/                 # ML models directory
│   └── log_classifier.joblib
├── resources/              # Input/output files
│   ├── test.csv
│   └── output.csv
├── training/               # Training notebooks and data
│   ├── log_classification.ipynb
│   └── dataset/
│       └── synthetic_logs.csv
├── logs/                   # Application logs (auto-created)
└── docs/                   # Documentation (auto-created)
    └── API.md
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem:** `ModuleNotFoundError` when starting the server
**Solution:** 
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python version (3.8+)

#### 2. BERT Model Loading Fails
**Problem:** `sentence-transformers` fails to download models
**Solution:**
- Check internet connection
- The app will gracefully degrade to regex + LLM classification
- Models are loaded lazily to prevent startup failures

#### 3. Groq API Errors
**Problem:** `GROQ_API_KEY` not found or invalid
**Solution:**
- Verify `.env` file exists and contains valid API key
- Check Groq console for API key status
- Ensure no extra spaces in the key

#### 4. File Upload Errors
**Problem:** CSV upload fails
**Solution:**
- Check file has required columns: `source`, `log_message`
- Verify file size is under the limit (default 10MB)
- Ensure file is UTF-8 encoded

#### 5. Port Already in Use
**Problem:** `Address already in use` error
**Solution:**
- Change port: `uvicorn server:app --port 8001`
- Kill existing process: `netstat -ano | findstr :8000` (Windows)

### Log Analysis
Check the `logs/` directory for detailed error information:
- `app.log`: Main application logs
- Logs rotate daily automatically

### Performance Issues
If classification is slow:
1. Check which methods are being used (logs show classification stats)
2. Consider adjusting `BERT_CONFIDENCE_THRESHOLD` to reduce LLM usage
3. Add more regex patterns for common log types

## Development Setup

### Code Style
The project follows PEP 8 style guidelines with comprehensive type hints.

### Testing
```bash
# Test individual components
python -c "from processor_regex import classify_with_regex; print('Regex OK')"
python -c "from processor_bert import classify_with_bert; print('BERT OK')"
python -c "from processor_llm import classify_with_llm; print('LLM OK')"

# Test full classification
python -c "from classification_service import classify_logs; print('Service OK')"
```

### Configuration Validation
The application validates configuration on startup and will exit with clear error messages if settings are invalid.

## Production Deployment

### Environment Variables
Set production values for:
- `GROQ_API_KEY`: Production API key
- `MAX_FILE_SIZE_MB`: Appropriate for your use case
- `OUTPUT_DIR`: Persistent storage location

### Security Considerations
- API key is loaded from environment variables only
- File uploads are validated for size and type
- Input sanitization prevents injection attacks
- Comprehensive error handling prevents information leakage

### Monitoring
- Health check endpoint for load balancer monitoring
- Structured logging for centralized log analysis
- Classification statistics for performance monitoring