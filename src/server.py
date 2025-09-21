from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api.api_routes import router
from src.utils.logger_config import setup_logging, get_logger
from src.core.config import config
from src.core.constants import API_METADATA

# Set up logging first
setup_logging()
logger = get_logger(__name__)

# Create FastAPI app with enhanced configuration
app = FastAPI(
    title=API_METADATA["title"],
    description=API_METADATA["description"],
    version=API_METADATA["version"],
    contact=API_METADATA["contact"],
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Serve static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Log configuration on startup
logger.info(f"Server starting with configuration: {config.to_dict()}")

@app.on_event("startup")
async def startup_event():
    """Log application startup and preload models."""
    # Log configuration
    config_summary = {
        'max_file_size_mb': config.max_file_size_mb,
        'allowed_file_types': config.allowed_file_types,
        'bert_model_name': config.bert_model_name,
        'llm_model_name': config.llm_model_name,
        'llm_temperature': config.llm_temperature,
        'bert_confidence_threshold': config.bert_confidence_threshold,
        'output_dir': config.output_dir,
        'legacy_sources': config.legacy_sources
    }
    logger.info(f"Server starting with configuration: {config_summary}")
    
    # Preload models to avoid cold start penalty (force synchronous loading)
    try:
        logger.info("Attempting to preload BERT model for faster initial requests...")
        from src.processors.processor_bert import load_models
        
        # Force synchronous loading to ensure models are ready
        logger.info("Loading BERT models synchronously...")
        if load_models():
            logger.info("BERT model preloaded successfully - ready for requests")
        else:
            logger.warning("BERT model loading failed - will use regex and LLM only")
            
        # Test BERT functionality
        try:
            from src.processors.processor_bert import classify_with_bert
            test_result = classify_with_bert("TestSource", "System error occurred")
            logger.info(f"BERT functionality test result: {test_result}")
        except Exception as e:
            logger.warning(f"BERT functionality test failed: {e}")
            
    except Exception as e:
        logger.warning(f"Model preloading failed: {str(e)}, will load on first request")
    
    logger.info("Log Classification API server started successfully")
    logger.info(f"API documentation available at /docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("Log Classification API server shutting down")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint serving the modern web frontend."""
    logger.debug("Frontend accessed")
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("Frontend files not found")
        return """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Log Classification API</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
                    .error { color: #ef4444; }
                    .info { color: #2563eb; }
                </style>
            </head>
            <body>
                <h1>🚀 Log Classification API</h1>
                <p class="error">Frontend files not found. Using fallback interface.</p>
                <p class="info">API Documentation: <a href="/docs">/docs</a></p>
                <p class="info">Health Check: <a href="/api/v1/health/">/api/v1/health/</a></p>
            </body>
        </html>
        """

@app.get("/app", response_class=HTMLResponse)
async def app_frontend():
    """Alternative route for the frontend."""
    return await root()

@app.get("/sample.csv")
async def download_sample_csv():
    """Download a sample CSV file for testing."""
    from fastapi.responses import Response
    
    sample_data = """source,log_message
WebServer,"ERROR: Database connection failed"
Application,"INFO: User login successful for user@example.com"
System,"WARNING: High memory usage detected: 85%"
Security,"ALERT: Failed login attempt from IP 192.168.1.100"
Database,"ERROR: Query timeout after 30 seconds"
API,"INFO: Request processed successfully in 120ms"
WebServer,"ERROR: 404 Not Found - /missing-page"
Application,"DEBUG: Cache hit for user session data"
System,"INFO: Backup completed successfully"
Security,"WARN: Multiple failed login attempts detected"
Database,"INFO: Connection pool size increased to 50"
API,"ERROR: Rate limit exceeded for client IP"
WebServer,"INFO: Server started on port 8080"
Application,"ERROR: Null pointer exception in user service"
System,"CRITICAL: Disk space below 5% on /var/log"""

    headers = {
        'Content-Disposition': 'attachment; filename="sample_logs.csv"',
        'Content-Type': 'text/csv'
    }
    
    logger.info("Sample CSV downloaded")
    return Response(content=sample_data, headers=headers)

# Legacy endpoint for backward compatibility
@app.post("/classify/")
async def legacy_classify_endpoint(file):
    """Legacy endpoint - redirects to new API structure."""
    logger.info("Legacy endpoint accessed, redirecting to new API")
    # Import here to avoid circular imports
    from fastapi import File, UploadFile
    from api.api_routes import classify_and_download
    return await classify_and_download(file)