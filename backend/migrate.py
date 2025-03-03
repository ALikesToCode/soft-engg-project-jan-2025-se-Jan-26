import asyncio
import logging
import os
from sqlalchemy import text, create_engine, MetaData, Table, Column, Integer, String, Text, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.database import Base
from app.models.user import User
from app.models.assignment import Assignment, Submission
from app.models.faq import FAQ
from app.models.system_settings import SystemSettings, Integration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def add_missing_columns():
    """Add missing columns to users table if they don't exist"""
    try:
        async with engine.begin() as conn:
            # Check if table exists
            check_table_query = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                );
            """)
            result = await conn.execute(check_table_query)
            table_exists = result.scalar()
            
            if not table_exists:
                logger.error("Users table does not exist. Please run the application first to create the table.")
                return
                
            # Define all columns that should be in the users table
            columns_to_check = [
                {"name": "id", "type": "UUID", "default": "uuid_generate_v4()", "nullable": False, "primary_key": True},
                {"name": "email", "type": "VARCHAR", "default": None, "nullable": True},
                {"name": "name", "type": "VARCHAR", "default": None, "nullable": True},
                {"name": "hashed_password", "type": "VARCHAR", "default": None, "nullable": True},
                {"name": "is_google_user", "type": "BOOLEAN", "default": "FALSE", "nullable": True},
                {"name": "picture", "type": "VARCHAR", "default": None, "nullable": True},
                {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP", "nullable": True},
                {"name": "updated_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP", "nullable": True},
                {"name": "role", "type": "VARCHAR", "default": "'student'", "nullable": True}
            ]
            
            # Check each column and add if missing
            for column in columns_to_check:
                check_column_query = text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = '{column["name"]}'
                """)
                result = await conn.execute(check_column_query)
                column_exists = result.scalar() is not None
                
                if not column_exists:
                    logger.info(f"Adding {column['name']} column to users table...")
                    
                    # Build the ALTER TABLE statement
                    default_clause = f"DEFAULT {column['default']}" if column['default'] else ""
                    nullable_clause = "NOT NULL" if not column['nullable'] else ""
                    primary_key_clause = "PRIMARY KEY" if column.get('primary_key') else ""
                    
                    add_column_query = text(f"""
                        ALTER TABLE users 
                        ADD COLUMN {column['name']} {column['type']} {default_clause} {nullable_clause} {primary_key_clause}
                    """)
                    
                    await conn.execute(add_column_query)
                    logger.info(f"Successfully added {column['name']} column to users table")
                else:
                    logger.info(f"{column['name']} column already exists in users table")
                    
            # Ensure the uuid-ossp extension is enabled for uuid_generate_v4()
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
            
    except Exception as e:
        logger.error(f"Error adding columns: {e}")
        raise

async def create_faq_table():
    """Create the FAQs table if it doesn't exist."""
    try:
        async with engine.begin() as conn:
            # Check if the table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'faqs'
                );
            """))
            exists = result.scalar()
            
            if not exists:
                # Create the uuid extension first
                await conn.execute(text("""
                    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
                """))
                
                # Then create the table
                await conn.execute(text("""
                    CREATE TABLE faqs (
                        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        question VARCHAR(500) NOT NULL,
                        answer TEXT NOT NULL,
                        category_id VARCHAR(50) NOT NULL,
                        priority INTEGER DEFAULT 0,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE
                    );
                """))
                logging.info("FAQs table created successfully.")
            else:
                logging.info("FAQs table already exists.")
    except Exception as e:
        logging.error(f"Error creating FAQs table: {e}")

# Create tables
async def create_tables():
    # Create async engine with SSL context
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Remove sslmode from URL and pass it as a parameter
    db_url = settings.DATABASE_URL
    if "sslmode=require" in db_url:
        db_url = db_url.replace("?sslmode=require", "")
    
    engine = create_async_engine(
        db_url,
        connect_args={"ssl": ssl_context} if "neon.tech" in db_url else {}
    )
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()

# Drop tables
async def drop_tables():
    # Create async engine with SSL context
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Remove sslmode from URL and pass it as a parameter
    db_url = settings.DATABASE_URL
    if "sslmode=require" in db_url:
        db_url = db_url.replace("?sslmode=require", "")
    
    engine = create_async_engine(
        db_url,
        connect_args={"ssl": ssl_context} if "neon.tech" in db_url else {}
    )
    
    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

# Reset tables (drop and create)
async def reset_tables():
    await drop_tables()
    await create_tables()

# Seed database with initial data
async def seed_database():
    # Create sync engine for raw SQL execution
    db_url = settings.DATABASE_URL.replace("+asyncpg", "")
    if "sslmode=require" in db_url:
        db_url = db_url.replace("?sslmode=require", "")
    
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    engine = create_engine(
        db_url,
        connect_args={"sslmode": "require"} if "neon.tech" in db_url else {}
    )
    
    # Insert sample users
    with engine.connect() as conn:
        conn.execute(text("""
        INSERT INTO users (id, email, hashed_password, name, role, created_at, updated_at)
        VALUES 
        (gen_random_uuid(), 'admin@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Admin User', 'admin', NOW(), NOW()),
        (gen_random_uuid(), 'faculty@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Faculty User', 'faculty', NOW(), NOW()),
        (gen_random_uuid(), 'student@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Student User', 'student', NOW(), NOW()),
        (gen_random_uuid(), 'support@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Support User', 'support', NOW(), NOW())
        """))
        
        # Insert sample system settings
        conn.execute(text("""
        INSERT INTO system_settings (key, value)
        VALUES 
        ('auth', '{"jwt_expiry": 24, "oauth_provider": "google", "mfa_enabled": false}'),
        ('notifications', '{"email_frequency": "immediate", "smtp_server": "smtp.example.com"}'),
        ('api', '{"rate_limit": 100, "data_retention_days": 30}')
        """))
        
        # Insert sample integrations
        conn.execute(text("""
        INSERT INTO integrations (name, type, endpoint, api_key, status)
        VALUES 
        ('Canvas LMS', 'lms', 'https://canvas.example.com/api', 'sample_api_key_1', 'active'),
        ('Stripe Payments', 'payment', 'https://api.stripe.com/v1', 'sample_api_key_2', 'active'),
        ('Google Analytics', 'analytics', 'https://analytics.google.com/api', 'sample_api_key_3', 'inactive')
        """))
        
        conn.commit()

# Main function
async def main():
    # Get command line arguments
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migrate.py [create|drop|reset|seed]")
        return
    
    command = sys.argv[1].lower()
    
    if command == "create":
        await create_tables()
        print("Tables created successfully")
    elif command == "drop":
        await drop_tables()
        print("Tables dropped successfully")
    elif command == "reset":
        await reset_tables()
        print("Tables reset successfully")
    elif command == "seed":
        await seed_database()
        print("Database seeded successfully")
    else:
        print("Unknown command. Use create, drop, reset, or seed")

if __name__ == "__main__":
    asyncio.run(main()) 