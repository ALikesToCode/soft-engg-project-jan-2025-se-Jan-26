#!/usr/bin/env python3
"""
Check database status and table content.

This script connects to the database and analyzes the structure and content of all tables.
It reports the number of rows in each table and identifies empty tables that might need mock data.
"""

import asyncio
import logging
import os
import sys
from collections import defaultdict
from dotenv import load_dotenv
import psycopg
from tabulate import tabulate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

async def get_connection():
    """Get a connection to the database."""
    # Load environment variables
    load_dotenv()
    
    # Get connection string
    connection_string = os.getenv("DATABASE_URL")
    if not connection_string:
        logger.error("DATABASE_URL environment variable is not set")
        return None
    
    # Ensure sslmode=require is present
    if "sslmode=require" not in connection_string:
        if "?" in connection_string:
            connection_string += "&sslmode=require"
        else:
            connection_string += "?sslmode=require"
    
    # Convert SQLAlchemy URL format to psycopg format if needed
    if "postgresql+asyncpg://" in connection_string:
        connection_string = connection_string.replace("postgresql+asyncpg://", "postgresql://")
    
    # Connect to the database
    return await psycopg.AsyncConnection.connect(connection_string)

async def check_tables():
    """Check all tables in the database and report their row counts"""
    # Load environment variables
    load_dotenv()
    
    # Get connection string
    connection_string = os.getenv("DATABASE_URL")
    if not connection_string:
        logger.error("DATABASE_URL environment variable is not set")
        return False
    
    # Ensure sslmode=require is present
    if "sslmode=require" not in connection_string:
        if "?" in connection_string:
            connection_string += "&sslmode=require"
        else:
            connection_string += "?sslmode=require"
    
    # Convert SQLAlchemy URL format to psycopg format if needed
    if "postgresql+asyncpg://" in connection_string:
        connection_string = connection_string.replace("postgresql+asyncpg://", "postgresql://")
    
    logger.info(f"Connecting to database...")
    
    try:
        # Connect to the database
        conn = await psycopg.AsyncConnection.connect(connection_string)
        
        # Get all tables in the database
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = await cur.fetchall()
            
            logger.info(f"Found {len(tables)} tables in the database:")
            
            # Prepare data for table display
            table_data = []
            empty_tables = []
            
            # Group tables by prefix to organize output
            table_groups = defaultdict(list)
            
            for table in tables:
                table_name = table[0]
                
                # Check row count
                await cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                result = await cur.fetchone()
                count = result[0]  # Fixed: properly await the coroutine
                
                # Store data
                table_data.append([table_name, count])
                
                # Track empty tables
                if count == 0:
                    empty_tables.append(table_name)
                
                # Group by prefix or the whole name if no clear prefix
                prefix = table_name.split('_')[0] if '_' in table_name else table_name
                table_groups[prefix].append((table_name, count))
            
            # Print table counts in a formatted table
            print("\nTable row counts:")
            print(tabulate(table_data, headers=["Table", "Row Count"], tablefmt="grid"))
            
            # Summarize empty tables
            if empty_tables:
                print("\nEmpty tables that might need mock data:")
                for table in empty_tables:
                    print(f"  - {table}")
            else:
                print("\nAll tables have data. No empty tables found.")
            
            # Print table groups
            print("\nTables grouped by category:")
            for prefix, tables in table_groups.items():
                print(f"\n{prefix.capitalize()} tables:")
                group_data = [[name, count] for name, count in tables]
                print(tabulate(group_data, headers=["Table", "Row Count"], tablefmt="simple"))
        
        # Close the connection
        await conn.close()
        logger.info("\nDatabase connection closed.")
        return True
    except Exception as e:
        logger.error(f"Error checking tables: {str(e)}")
        return False

async def describe_table_structure(table_name):
    """
    Describe the structure of a specific table.
    
    Args:
        table_name: The name of the table to describe
    """
    conn = None
    try:
        conn = await get_connection()
        async with conn.cursor() as cur:
            # Get column information
            await cur.execute("""
                SELECT column_name, data_type, column_default, 
                       is_nullable
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            columns = await cur.fetchall()
            
            # Get foreign key information
            await cur.execute("""
                SELECT kcu.column_name, 
                       ccu.table_name || '(' || ccu.column_name || ')' as references
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu 
                  ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = %s
            """, (table_name,))
            foreign_keys = await cur.fetchall()
            
            # Check if table has any rows
            await cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            result = await cur.fetchone()
            count = result[0]
            
            # Display table structure
            print(f"\nStructure of table '{table_name}':")
            
            # Format and display column info
            headers = ["Column", "Type", "Default", "Nullable"]
            table_data = [(col[0], col[1], col[2] or "-", "YES" if col[3] == "YES" else "NO") 
                         for col in columns]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            # Display foreign keys
            if foreign_keys:
                print("\nForeign Keys:")
                fk_headers = ["Column", "References"]
                fk_data = [(fk[0], fk[1]) for fk in foreign_keys]
                print(tabulate(fk_data, headers=fk_headers, tablefmt="simple"))
            
            # Show sample data if table is not empty
            if count > 0:
                await cur.execute(f"SELECT * FROM {table_name} LIMIT 5")
                sample_data = await cur.fetchall()
                
                # Get column names for the headers
                column_names = [col[0] for col in columns]
                
                print(f"\nSample data (up to 5 rows):")
                print(tabulate(sample_data, headers=column_names, tablefmt="grid"))
            else:
                print("\nNo data found in this table.")
    except Exception as e:
        logging.error(f"Error describing table '{table_name}': {str(e)}")
    finally:
        if conn:
            await conn.close()

async def main():
    """Main function"""
    if len(sys.argv) > 1:
        # If table name is provided as argument, describe that table
        await describe_table_structure(sys.argv[1])
    else:
        # Otherwise check all tables
        await check_tables()

if __name__ == "__main__":
    logger.info("Starting database inspection...")
    asyncio.run(main()) 