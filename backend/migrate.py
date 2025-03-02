import asyncio
import logging
from sqlalchemy import text
from app.database import engine

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

async def main():
    """Run all migration functions"""
    await add_missing_columns()
    await create_faq_table()
    logger.info("All migrations completed successfully.")

if __name__ == "__main__":
    asyncio.run(main()) 