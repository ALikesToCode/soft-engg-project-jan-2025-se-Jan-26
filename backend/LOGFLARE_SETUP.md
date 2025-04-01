# Logflare Integration

This document provides instructions on how to set up and use Logflare for logging in the application.

## Overview

Logflare is a cloud-based log management service that allows you to collect, analyze, and visualize logs from your application. This integration sends logs from the application to Logflare, where you can view and analyze them.

## Configuration

### Environment Variables

To enable Logflare logging, you need to set the following environment variables in your `.env` file:

```
USE_LOGFLARE=true
LOGFLARE_SOURCE_ID=b12c0a76-5b1a-4a58-93bc-e5340168165d
LOGFLARE_API_KEY=7sniujkFTAmT
LOGFLARE_BATCH_SIZE=10
LOGFLARE_LOG_LEVEL=INFO
```

- `USE_LOGFLARE`: Set to `true` to enable Logflare logging, or `false` to disable it.
- `LOGFLARE_SOURCE_ID`: Your Logflare source ID.
- `LOGFLARE_API_KEY`: Your Logflare API key.
- `LOGFLARE_BATCH_SIZE`: Number of logs to batch before sending to Logflare.
- `LOGFLARE_LOG_LEVEL`: The minimum log level to send to Logflare (DEBUG, INFO, WARNING, ERROR, CRITICAL).

### Testing the Integration

You can test the Logflare integration by running the `test_logflare.py` script:

```bash
cd backend
python test_logflare.py
```

This script will send test logs to Logflare and print a link to the Logflare dashboard where you can view the logs.

## Viewing Logs

You can view your logs in the Logflare dashboard at:

```
https://logflare.app/sources/b12c0a76-5b1a-4a58-93bc-e5340168165d
```

## Using Logflare in Your Code

To log messages to Logflare, use the standard Python logging module:

```python
import logging

# Get a logger for your module
logger = logging.getLogger(__name__)

# Log messages
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")

# Log with extra data
logger.info(
    "This is a message with extra data",
    extra={
        "user_id": "123456",
        "action": "login",
        "data": {
            "key1": "value1",
            "key2": "value2"
        }
    }
)
```

## Troubleshooting

If you're not seeing logs in Logflare:

1. Check that `USE_LOGFLARE` is set to `true` in your `.env` file.
2. Verify that your `LOGFLARE_SOURCE_ID` and `LOGFLARE_API_KEY` are correct.
3. Check that your application has internet access to send logs to Logflare.
4. Look for any error messages in the console or application logs.

## Additional Resources

- [Logflare Documentation](https://docs.logflare.app/)
- [Logflare Dashboard](https://logflare.app/dashboard)
- [Logflare API Reference](https://docs.logflare.app/api-reference/) 