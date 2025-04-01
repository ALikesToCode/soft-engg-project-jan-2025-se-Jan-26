#!/usr/bin/env python3
"""
Script to create an S3 bucket for file uploads.
This is useful for setting up the storage for the first time.
"""

import os
import sys
import boto3
from botocore.exceptions import ClientError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# S3 Configuration
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")
S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_REGION = os.environ.get("S3_REGION", "auto")

def create_bucket():
    """Create an S3 bucket if it doesn't exist."""
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=S3_REGION
        )
        
        # Check if bucket exists
        try:
            s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
            logger.info(f"Bucket '{S3_BUCKET_NAME}' already exists.")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                logger.info(f"Creating bucket '{S3_BUCKET_NAME}'...")
                
                # For most S3 providers, you'd use this:
                # s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
                
                # For Cloudflare R2, which doesn't support regions in the same way:
                s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
                
                logger.info(f"Bucket '{S3_BUCKET_NAME}' created successfully.")
                return True
            else:
                # Other error
                logger.error(f"Error checking bucket: {e}")
                return False
    
    except Exception as e:
        logger.error(f"Failed to initialize S3 client or create bucket: {e}")
        return False

def test_bucket_access():
    """Test access to the bucket by uploading and deleting a test file."""
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=S3_REGION
        )
        
        # Upload a test file
        test_key = "test/test_file.txt"
        test_content = b"This is a test file to verify S3 bucket access."
        
        logger.info(f"Uploading test file to '{S3_BUCKET_NAME}/{test_key}'...")
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=test_key,
            Body=test_content
        )
        
        # Verify the file exists
        logger.info("Verifying test file...")
        response = s3_client.get_object(
            Bucket=S3_BUCKET_NAME,
            Key=test_key
        )
        content = response['Body'].read()
        
        if content == test_content:
            logger.info("Test file content verified successfully.")
        else:
            logger.warning("Test file content does not match!")
        
        # Delete the test file
        logger.info("Deleting test file...")
        s3_client.delete_object(
            Bucket=S3_BUCKET_NAME,
            Key=test_key
        )
        
        logger.info("Test file deleted successfully.")
        logger.info("S3 bucket access test completed successfully.")
        return True
    
    except Exception as e:
        logger.error(f"Failed to test bucket access: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting S3 bucket setup...")
    
    if create_bucket():
        logger.info("Bucket creation/verification successful.")
        
        if test_bucket_access():
            logger.info("Bucket access test successful.")
            logger.info("S3 storage is ready for use.")
            sys.exit(0)
        else:
            logger.error("Bucket access test failed.")
            sys.exit(1)
    else:
        logger.error("Bucket creation/verification failed.")
        sys.exit(1) 