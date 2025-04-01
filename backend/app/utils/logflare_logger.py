import logging
import json
import requests
from datetime import datetime, UTC
from typing import Dict, Any, Optional
from app.config import settings

class LogflareHandler(logging.Handler):
    """
    A custom logging handler that sends logs to Logflare.
    """
    def __init__(self, source_id: str, api_key: str, batch_size: int = 10, level=logging.NOTSET):
        """
        Initialize the Logflare handler.
        
        Args:
            source_id: The Logflare source ID
            api_key: The Logflare API key
            batch_size: Number of logs to batch before sending
            level: The logging level
        """
        super().__init__(level)
        self.source_id = source_id
        self.api_key = api_key
        self.batch_size = batch_size
        self.log_buffer = []
        self.endpoint = f"https://api.logflare.app/logs/json?source={source_id}"
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': api_key
        }
    
    def emit(self, record: logging.LogRecord):
        """
        Emit a log record to Logflare.
        
        Args:
            record: The log record to emit
        """
        try:
            # Format the log message
            log_entry = self.format_log_entry(record)
            
            # Add to buffer
            self.log_buffer.append(log_entry)
            
            # Send if buffer is full
            if len(self.log_buffer) >= self.batch_size:
                self.flush()
        except Exception as e:
            self.handleError(record)
    
    def format_log_entry(self, record: logging.LogRecord) -> Dict[str, Any]:
        """
        Format a log record as a Logflare-compatible JSON object.
        
        Args:
            record: The log record to format
            
        Returns:
            A dictionary representing the log entry
        """
        # Get the log message
        if isinstance(record.msg, dict):
            message = record.msg
        else:
            message = self.format(record)
        
        # Extract exception info if available
        exc_info = None
        if record.exc_info:
            exc_type, exc_value, exc_traceback = record.exc_info
            exc_info = {
                'type': exc_type.__name__ if exc_type else None,
                'value': str(exc_value) if exc_value else None,
                'traceback': self.formatException(record.exc_info) if exc_traceback else None
            }
        
        # Create the log entry
        entry = {
            'message': message,
            'level': record.levelname,
            'timestamp': datetime.now(UTC).isoformat() + 'Z',
            'logger': record.name,
            'pathname': record.pathname,
            'lineno': record.lineno,
            'funcName': record.funcName,
            'threadName': record.threadName,
            'process': record.process,
            'app_name': settings.APP_NAME,
            'app_version': settings.APP_VERSION,
            'environment': settings.ENV
        }
        
        # Add exception info if available
        if exc_info:
            entry['exception'] = exc_info
        
        # Add extra fields if available
        if hasattr(record, 'extra') and record.extra:
            entry.update(record.extra)
        
        return entry
    
    def formatException(self, exc_info):
        """
        Format an exception info tuple into a string.
        
        Args:
            exc_info: The exception info tuple
            
        Returns:
            A formatted string representation of the exception
        """
        import traceback
        return ''.join(traceback.format_exception(*exc_info))
    
    def flush(self):
        """
        Flush the log buffer by sending logs to Logflare.
        """
        if not self.log_buffer:
            return
        
        try:
            # Send logs to Logflare
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=self.log_buffer,
                timeout=5
            )
            
            # Check if the request was successful
            if response.status_code != 200:
                print(f"Failed to send logs to Logflare: {response.status_code} - {response.text}")
            
            # Clear the buffer
            self.log_buffer = []
        except Exception as e:
            print(f"Error sending logs to Logflare: {str(e)}")
    
    def close(self):
        """
        Close the handler and flush any remaining logs.
        """
        self.flush()
        super().close()


def setup_logflare_logging(
    source_id: str,
    api_key: str,
    level: int = logging.INFO,
    batch_size: int = 10,
    formatter: Optional[logging.Formatter] = None
):
    """
    Set up logging with Logflare.
    
    Args:
        source_id: The Logflare source ID
        api_key: The Logflare API key
        level: The logging level
        batch_size: Number of logs to batch before sending
        formatter: Custom formatter for logs
    
    Returns:
        The configured logger
    """
    # Create the Logflare handler
    handler = LogflareHandler(source_id, api_key, batch_size, level)
    
    # Set formatter
    if formatter is None:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
    
    return root_logger 