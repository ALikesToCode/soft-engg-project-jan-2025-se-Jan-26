"""
Test script for Logflare integration.

This script tests the Logflare integration by sending test logs.
"""

import logging
import time
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.utils.logflare_logger import LogflareHandler

def test_logflare():
    """Test the Logflare integration."""
    # Configure settings
    settings.USE_LOGFLARE = True
    settings.LOGFLARE_SOURCE_ID = "b12c0a76-5b1a-4a58-93bc-e5340168165d"
    settings.LOGFLARE_API_KEY = "7sniujkFTAmT"
    
    # Configure logging
    logger = logging.getLogger("test_logflare")
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
    
    # Add Logflare handler
    logflare_handler = LogflareHandler(
        source_id=settings.LOGFLARE_SOURCE_ID,
        api_key=settings.LOGFLARE_API_KEY,
        batch_size=1  # Send logs immediately
    )
    logflare_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(logflare_handler)
    
    # Log test messages
    logger.info("This is a test INFO message")
    logger.warning("This is a test WARNING message")
    logger.error("This is a test ERROR message")
    
    # Log with extra data
    logger.info(
        "This is a test message with extra data",
        extra={
            "user_id": "123456",
            "action": "test",
            "data": {
                "key1": "value1",
                "key2": "value2"
            }
        }
    )
    
    # Wait for logs to be sent
    time.sleep(2)
    
    # Flush and close the handler
    logflare_handler.flush()
    logflare_handler.close()
    
    print("Test completed. Check the Logflare dashboard at:")
    print(f"https://logflare.app/sources/{settings.LOGFLARE_SOURCE_ID}")

if __name__ == "__main__":
    test_logflare() 