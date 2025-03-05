import logging
import os
from logging.handlers import RotatingFileHandler
from app.config import settings
from pathlib import Path

# Try to import the Logflare handler
try:
    from app.utils.logflare_logger import LogflareHandler, setup_logflare_logging
    LOGFLARE_AVAILABLE = True
except ImportError:
    LOGFLARE_AVAILABLE = False


def get_log_level(level_name: str) -> int:
    """
    Convert a log level name to its numeric value.
    
    Args:
        level_name: The name of the log level (e.g., 'INFO', 'DEBUG')
        
    Returns:
        The numeric value of the log level
    """
    level_map = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'NOTSET': logging.NOTSET
    }
    return level_map.get(level_name.upper(), logging.INFO)


def configure_logging():
    """
    Configure the logging system.
    
    This function sets up logging with both file and console handlers.
    If Logflare is enabled, it also adds a Logflare handler.
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add Logflare handler if enabled
    if settings.USE_LOGFLARE and LOGFLARE_AVAILABLE:
        log_level = get_log_level(settings.LOGFLARE_LOG_LEVEL)
        
        # Create Logflare handler
        logflare_handler = LogflareHandler(
            source_id=settings.LOGFLARE_SOURCE_ID,
            api_key=settings.LOGFLARE_API_KEY,
            batch_size=settings.LOGFLARE_BATCH_SIZE,
            level=log_level
        )
        logflare_handler.setFormatter(formatter)
        root_logger.addHandler(logflare_handler)
        
        # Log that Logflare is enabled
        root_logger.info("Logflare logging enabled")
    else:
        # Only add file handler if Logflare is not enabled
        # Determine log file path
        log_file = log_dir / "app.log"
        
        # Add file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Add console handler (always add this regardless of Logflare)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    configure_specific_loggers()
    
    return root_logger


def configure_specific_loggers():
    """
    Configure specific loggers with custom settings.
    """
    # Configure uvicorn access logger
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.setLevel(logging.INFO)
    
    # Configure SQLAlchemy logger
    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    sqlalchemy_logger.setLevel(logging.WARNING)
    
    # Configure FastAPI logger
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.setLevel(logging.INFO)
    
    # Configure app loggers
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO) 