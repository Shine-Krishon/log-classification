# 📁 Log Classification System - Project Structure

## 🏗️ Organized Folder Structure

```
project-nlp-log-classification/
├── 📁 src/                          # Main source code
│   ├── 📁 api/                      # API routes and endpoints
│   │   ├── __init__.py
│   │   └── api_routes.py            # FastAPI routes
│   ├── 📁 core/                     # Core application logic
│   │   ├── __init__.py
│   │   ├── config.py                # Configuration management
│   │   ├── constants.py             # Application constants
│   │   └── models.py                # Pydantic models
│   ├── 📁 processors/               # Log classification processors
│   │   ├── __init__.py
│   │   ├── processor_bert.py        # BERT-based classification
│   │   ├── processor_llm.py         # LLM-based classification
│   │   └── processor_regex.py       # Regex-based classification
│   ├── 📁 services/                 # Business logic services
│   │   ├── __init__.py
│   │   ├── classification_service.py # Main classification orchestrator
│   │   ├── cache_manager.py         # Caching service
│   │   ├── performance_monitor.py   # Advanced performance monitoring
│   │   └── performance_monitor_simple.py # Simple performance monitoring
│   ├── 📁 utils/                    # Utility functions
│   │   ├── __init__.py
│   │   ├── logger_config.py         # Logging configuration
│   │   └── utils.py                 # General utilities
│   ├── __init__.py
│   └── server.py                    # FastAPI application server
├── 📁 frontend/                     # Web frontend
│   ├── index.html                   # Main HTML file
│   └── 📁 static/
│       ├── 📁 css/
│       │   └── main.css             # Stylesheet
│       └── 📁 js/
│           └── main.js              # JavaScript application logic
├── 📁 tests/                        # Test files
│   ├── test_api.py                  # API tests
│   ├── test_comprehensive.py       # Comprehensive test suite
│   ├── test_focused.py              # Focused unit tests
│   ├── test_frontend_api.py         # Frontend API tests
│   ├── test_performance.py         # Performance tests
│   ├── test_quick.py                # Quick smoke tests
│   ├── test_status_report.py       # Status reporting tests
│   ├── test_logs.csv               # Test data
│   ├── test_logs_detailed.csv      # Detailed test data
│   ├── test_perf.csv               # Performance test data
│   └── test_upload.csv             # Upload test data
├── 📁 data/                         # Data and resources
│   ├── 📁 resources/                # Static resources
│   │   ├── arch.png                # Architecture diagram
│   │   ├── output.csv              # Sample output
│   │   └── test.csv                # Test dataset
│   └── 📁 training/                 # Training data and notebooks
│       ├── log_classification.ipynb # Training notebook
│       └── 📁 dataset/
│           └── synthetic_logs.csv   # Training dataset
├── 📁 config/                       # Configuration files
│   ├── Dockerfile                  # Docker container configuration
│   ├── docker-compose.yml          # Docker Compose setup
│   ├── nginx.conf                  # Nginx configuration
│   ├── requirements.txt            # Python dependencies
│   └── .env.example                # Environment variables template
├── 📁 scripts/                      # Utility scripts
│   ├── classify.py                 # Standalone classification script
│   ├── frontend_error_fix_summary.py # Frontend error fix summary
│   └── frontend_implementation_summary.py # Frontend implementation summary
├── 📁 docs/                         # Documentation
│   ├── API_DOCUMENTATION.md        # API documentation
│   ├── CODE_DOCUMENTATION.md       # Code documentation
│   ├── DEPLOYMENT_GUIDE.md         # Deployment guide
│   ├── FRONTEND_GUIDE.md           # Frontend guide
│   ├── PERFORMANCE_PHASE_COMPLETE.md # Performance phase documentation
│   └── PROJECT_COMPLETE.md         # Project completion documentation
├── 📁 models/                       # Trained models
│   └── log_classifier.joblib       # Trained classifier model
├── 📁 cache/                        # Cache directory (created at runtime)
├── 📁 logs/                         # Log files (created at runtime)
├── main.py                         # Main entry point
├── README.md                       # Project README
├── .env                            # Environment variables (not in git)
├── .gitignore                      # Git ignore rules
└── .dockerignore                   # Docker ignore rules
```

## 🎯 Benefits of This Structure

### 🔧 **Improved Maintainability**
- Clear separation of concerns
- Easy to locate specific functionality
- Logical grouping of related files

### 📦 **Better Package Management**
- Proper Python package structure with `__init__.py` files
- Clean import paths using relative imports
- Reduced circular import risks

### 🧪 **Enhanced Testing**
- All tests in dedicated `tests/` folder
- Test data organized separately
- Easy to run specific test suites

### 🚀 **Simplified Deployment**
- Configuration files grouped in `config/`
- Clear entry point with `main.py`
- Docker and deployment files organized

### 📚 **Better Documentation**
- All documentation in `docs/` folder
- Easy to find guides and references
- Structured project information

## 🔄 **How to Use**

### Start the Server:
```bash
python main.py
```

### Run Tests:
```bash
python -m pytest tests/
```

### Build Docker:
```bash
docker-compose -f config/docker-compose.yml up
```

This organized structure makes the project more professional, maintainable, and easier to understand for new developers!