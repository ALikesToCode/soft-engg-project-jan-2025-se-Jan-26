#!/usr/bin/env python3
"""
Redis Connection Test Script

This script tests the connection to Redis with the provided credentials.
It helps diagnose authentication issues with Redis.

Usage:
    python test_redis_connection.py [--password PASSWORD]

If no password is provided, it will try to read from the .env file.
"""

import os
import sys
import argparse
import redis
from dotenv import load_dotenv

def test_redis_connection(host, port, username=None, password=None, db=0):
    """Test connection to Redis server"""
    print(f"Testing connection to Redis at {host}:{port}...")
    
    try:
        # Create connection parameters
        params = {
            "host": host,
            "port": port,
            "db": db,
            "socket_timeout": 5,
            "decode_responses": True
        }
        
        if username and username != 'default':
            params["username"] = username
            
        if password:
            params["password"] = password
            
        # Try to connect
        r = redis.Redis(**params)
        
        # Test connection with ping
        response = r.ping()
        if response:
            print("✅ Connection successful!")
            print("Redis info:")
            info = r.info()
            print(f"  - Redis version: {info.get('redis_version', 'unknown')}")
            print(f"  - Connected clients: {info.get('connected_clients', 'unknown')}")
            print(f"  - Memory used: {info.get('used_memory_human', 'unknown')}")
            return True
        else:
            print("❌ Connection failed: Ping returned False")
            return False
            
    except redis.exceptions.AuthenticationError as e:
        print(f"❌ Authentication error: {e}")
        print("The Redis server requires a password, but the provided password was incorrect or missing.")
        return False
    except redis.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("Could not connect to the Redis server. Check if the host and port are correct.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test Redis connection")
    parser.add_argument("--password", help="Redis password")
    parser.add_argument("--username", help="Redis username")
    parser.add_argument("--host", help="Redis host")
    parser.add_argument("--port", type=int, help="Redis port")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get connection parameters
    host = args.host or os.getenv("REDIS_HOST") or "localhost"
    port = args.port or int(os.getenv("REDIS_PORT", "6379"))
    username = args.username or os.getenv("REDIS_USERNAME", "default")
    password = args.password or os.getenv("REDIS_PASSWORD")
    db = int(os.getenv("REDIS_DB", "0"))
    
    # Test connection
    success = test_redis_connection(host, port, username, password, db)
    
    # If connection failed and we're using Redis Cloud, try to extract password from URL
    if not success and "redns.redis-cloud.com" in host:
        print("\nTrying to extract password from REDIS_URL...")
        redis_url = os.getenv("REDIS_URL", "")
        if "://" in redis_url:
            try:
                # Try to extract password from URL
                from urllib.parse import urlparse
                parsed = urlparse(redis_url)
                extracted_username = parsed.username or "default"
                extracted_password = parsed.password
                
                if extracted_password:
                    print(f"Found credentials in REDIS_URL: username={extracted_username}, password={extracted_password}")
                    success = test_redis_connection(host, port, extracted_username, extracted_password, db)
                else:
                    print("No password found in REDIS_URL")
            except Exception as e:
                print(f"Error parsing REDIS_URL: {e}")
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 