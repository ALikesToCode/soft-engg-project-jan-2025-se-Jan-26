#!/usr/bin/env python3
"""
Script to set up CORS configuration for the S3 bucket.
This is important for browser-based uploads to work correctly.
"""

import os
import sys
import boto3
from botocore.exceptions import ClientError
import logging
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# S3 Configuration
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")
S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_REGION = os.environ.get("S3_REGION", "auto")

def check_env_vars():
    """Check if all required environment variables are set."""
    missing_vars = []
    if not S3_ACCESS_KEY:
        missing_vars.append("S3_ACCESS_KEY")
    if not S3_SECRET_KEY:
        missing_vars.append("S3_SECRET_KEY")
    if not S3_ENDPOINT_URL:
        missing_vars.append("S3_ENDPOINT_URL")
    if not S3_BUCKET_NAME:
        missing_vars.append("S3_BUCKET_NAME")
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your environment or .env file")
        return False
    return True

def setup_cors():
    """Set up CORS configuration for the S3 bucket."""
    if not check_env_vars():
        return False
        
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=S3_REGION
        )
        
        # Define CORS configuration
        cors_configuration = {
            'CORSRules': [
                {
                    'AllowedHeaders': ['*'],
                    'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                    'AllowedOrigins': ['*'],  # In production, you should restrict this to your frontend domains
                    'ExposeHeaders': ['ETag', 'Content-Length', 'Content-Type'],
                    'MaxAgeSeconds': 3000
                }
            ]
        }
        
        # Apply CORS configuration
        s3_client.put_bucket_cors(
            Bucket=S3_BUCKET_NAME,
            CORSConfiguration=cors_configuration
        )
        
        logger.info(f"CORS configuration applied to bucket '{S3_BUCKET_NAME}' successfully.")
        return True
    
    except ClientError as e:
        logger.error(f"Error setting up CORS: {e}")
        return False

if __name__ == "__main__":
    logger.info("Setting up CORS for S3 bucket...")
    
    if setup_cors():
        logger.info("CORS setup successful.")
        sys.exit(0)
    else:
        logger.error("CORS setup failed.")
        sys.exit(1) 