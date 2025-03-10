#!/usr/bin/env python3
"""
PostgreSQL Connection Test Script

This script tests the connection to PostgreSQL with the provided credentials.
It helps diagnose connection and schema issues with PostgreSQL.

Usage:
    python test_db_connection.py

The script will read connection parameters from the .env file.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from urllib.parse import urlparse, parse_qs

async def test_db_connection(database_url):
    """Test connection to PostgreSQL database"""
    print(f"Testing connection to PostgreSQL...")
    
    # Parse the database URL
    url = urlparse(database_url)
    query_params = parse_qs(url.query)
    
    # Extract components
    host = url.hostname
    port = url.port or 5432
    username = url.username
    password = url.password
    database = url.path.lstrip('/')
    
    print(f"Connection details:")
    print(f"  - Host: {host}")
    print(f"  - Port: {port}")
    print(f"  - Username: {username}")
    print(f"  - Database: {database}")
    print(f"  - SSL Mode: {query_params.get('sslmode', ['prefer'])[0]}")
    
    # Remove sslmode from the URL and handle it in connect_args
    ssl_mode = query_params.pop('sslmode', ['prefer'])[0]
    
    try:
        # Create engine
        engine = create_async_engine(
            database_url.replace("postgres://", "postgresql+asyncpg://"),
            future=True,
            echo=False,
            connect_args={
                "ssl": ssl_mode == "require",
                "server_settings": {
                    "search_path": "public"
                }
            }
        )
        
        # Test connection
        async with engine.begin() as conn:
            # Get PostgreSQL version
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"\n✅ Connection successful!")
            print(f"PostgreSQL version: {version}")
            
            # Check current schema
            result = await conn.execute(text("SELECT current_schema()"))
            schema = result.scalar()
            print(f"Current schema: {schema}")
            
            # List schemas
            result = await conn.execute(text("SELECT schema_name FROM information_schema.schemata"))
            schemas = [row[0] for row in result.fetchall()]
            print(f"Available schemas: {', '.join(schemas)}")
            
            # Try to create a schema
            try:
                await conn.execute(text("CREATE SCHEMA IF NOT EXISTS public"))
                print("✅ Schema creation successful")
            except Exception as e:
                print(f"❌ Schema creation failed: {e}")
            
            # Try to create an enum type
            try:
                await conn.execute(text("CREATE TYPE test_enum AS ENUM ('TEST1', 'TEST2')"))
                print("✅ Enum type creation successful")
                # Clean up
                await conn.execute(text("DROP TYPE test_enum"))
            except Exception as e:
                if "already exists" in str(e):
                    print("✅ Enum type already exists (this is fine)")
                else:
                    print(f"❌ Enum type creation failed: {e}")
            
            # List tables
            result = await conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = current_schema()"
            ))
            tables = [row[0] for row in result.fetchall()]
            if tables:
                print(f"Existing tables: {', '.join(tables)}")
            else:
                print("No tables found in the current schema")
                
            return True
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

async def main():
    # Load environment variables
    load_dotenv()
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    # Test connection
    success = await test_db_connection(database_url)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main()) 