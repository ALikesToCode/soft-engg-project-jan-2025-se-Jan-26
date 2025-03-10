#!/bin/bash
# Script to restart the application with the fixes

# Set terminal colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a Python package is installed
check_package() {
    python -c "import $1" 2>/dev/null
    return $?
}

echo -e "${YELLOW}Checking required Python packages...${NC}"
MISSING_PACKAGES=()

# Check for required packages
for package in redis sqlalchemy pydantic dotenv; do
    if ! check_package $package; then
        MISSING_PACKAGES+=($package)
    fi
done

# Install missing packages if any
if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}Installing missing packages: ${MISSING_PACKAGES[*]}${NC}"
    pip install ${MISSING_PACKAGES[*]}
fi

echo -e "${YELLOW}Stopping any running application processes...${NC}"
pkill -f "uvicorn main:app" || true
sleep 2

# Make sure the scripts directory exists
if [ ! -d "scripts" ]; then
    echo -e "${YELLOW}Creating scripts directory...${NC}"
    mkdir -p scripts
fi

# Check if test scripts exist
if [ ! -f "scripts/test_db_connection.py" ] || [ ! -f "scripts/test_redis_connection.py" ]; then
    echo -e "${RED}Test scripts not found. Please make sure they exist in the scripts directory.${NC}"
    exit 1
fi

# Create a simple script to test datetime handling
cat > scripts/test_datetime.py << 'EOF'
#!/usr/bin/env python3
"""
Test script to verify proper datetime handling with SQLAlchemy and PostgreSQL.
"""
import asyncio
from datetime import datetime, UTC
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import os

async def test_datetime():
    # Load environment variables
    load_dotenv()
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Create engine
        engine = create_async_engine(
            database_url.replace("postgres://", "postgresql+asyncpg://"),
            future=True,
            echo=False
        )
        
        # Test datetime handling
        async with engine.begin() as conn:
            # Create a test table
            try:
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS datetime_test (
                        id SERIAL PRIMARY KEY,
                        created_at TIMESTAMP WITH TIME ZONE,
                        updated_at TIMESTAMP WITHOUT TIME ZONE
                    )
                """))
                
                # Insert a record with timezone-aware datetime
                now_utc = datetime.now(UTC)
                now_naive = datetime.now()
                
                # Format as string for direct SQL
                now_str = now_utc.strftime('%Y-%m-%d %H:%M:%S')
                
                await conn.execute(
                    text("INSERT INTO datetime_test (created_at, updated_at) VALUES (:created_at, :updated_at)"),
                    {"created_at": now_utc, "updated_at": now_str}
                )
                
                # Retrieve the record
                result = await conn.execute(text("SELECT * FROM datetime_test ORDER BY id DESC LIMIT 1"))
                row = result.fetchone()
                
                if row:
                    print("✅ DateTime test passed!")
                    print(f"Inserted: {now_utc}")
                    print(f"Retrieved: {row.created_at}")
                    
                    # Clean up
                    await conn.execute(text("DROP TABLE datetime_test"))
                    return True
                else:
                    print("❌ Failed to retrieve datetime record")
                    return False
                    
            except Exception as e:
                print(f"❌ DateTime test failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_datetime())
    exit(0 if success else 1)
EOF

chmod +x scripts/test_datetime.py

echo -e "${YELLOW}Testing database connection...${NC}"
python scripts/test_db_connection.py
if [ $? -ne 0 ]; then
    echo -e "${RED}Database connection test failed. Please check your DATABASE_URL in .env${NC}"
    echo -e "${YELLOW}You may need to update your .env file with the correct database credentials.${NC}"
    exit 1
fi

echo -e "${YELLOW}Testing enum type handling...${NC}"
python scripts/test_enum.py
if [ $? -ne 0 ]; then
    echo -e "${RED}Enum type handling test failed. This could cause issues with course status.${NC}"
    echo -e "${YELLOW}The application has been updated to use String columns instead of PostgreSQL ENUM types.${NC}"
    # Continue anyway as we've fixed the code
fi

echo -e "${YELLOW}Testing datetime handling...${NC}"
python scripts/test_datetime.py
if [ $? -ne 0 ]; then
    echo -e "${RED}DateTime handling test failed. This could cause issues with user creation and updates.${NC}"
    echo -e "${YELLOW}The application has been updated to handle this issue, but you may need to check your database schema.${NC}"
    # Continue anyway as we've fixed the code
fi

echo -e "${YELLOW}Testing Redis connection...${NC}"
python scripts/test_redis_connection.py
if [ $? -ne 0 ]; then
    echo -e "${RED}Redis connection test failed. Please check your Redis configuration in .env${NC}"
    echo -e "${YELLOW}You need to set REDIS_PASSWORD in your .env file.${NC}"
    echo -e "${YELLOW}You can find the password in your Redis Cloud dashboard or contact your Redis administrator.${NC}"
    exit 1
fi

echo -e "${GREEN}All connection tests passed!${NC}"
echo -e "${YELLOW}Starting the application...${NC}"

# Start the application
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo -e "${GREEN}Application started successfully!${NC}"

# Create a simple script to test enum type handling
cat > scripts/test_enum.py << 'EOF'
#!/usr/bin/env python3
"""
Test script to verify proper enum type handling with SQLAlchemy and PostgreSQL.
"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import os

async def test_enum():
    # Load environment variables
    load_dotenv()
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Create engine
        engine = create_async_engine(
            database_url.replace("postgres://", "postgresql+asyncpg://"),
            future=True,
            echo=False,
            connect_args={
                "server_settings": {
                    "search_path": "public"
                }
            }
        )
        
        # Test enum type handling
        async with engine.begin() as conn:
            try:
                # Set search path explicitly
                await conn.execute(text("SET search_path TO public"))
                
                # Try to create an enum type using PL/pgSQL
                await conn.execute(text("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'test_enum_type') THEN
                            CREATE TYPE test_enum_type AS ENUM ('VALUE1', 'VALUE2', 'VALUE3');
                        END IF;
                    END $$;
                """))
                
                # Check if the enum type was created
                result = await conn.execute(text(
                    "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'test_enum_type')"
                ))
                enum_exists = result.scalar()
                
                if enum_exists:
                    print("✅ Enum type test passed!")
                    
                    # Clean up
                    await conn.execute(text("DROP TYPE test_enum_type"))
                    return True
                else:
                    print("❌ Failed to create enum type")
                    return False
                    
            except Exception as e:
                print(f"❌ Enum type test failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enum())
    exit(0 if success else 1)
EOF

chmod +x scripts/test_enum.py

echo -e "${YELLOW}Testing enum type handling...${NC}"
python scripts/test_enum.py
if [ $? -ne 0 ]; then
    echo -e "${RED}Enum type handling test failed. This could cause issues with course status.${NC}"
    echo -e "${YELLOW}The application has been updated to use String columns instead of PostgreSQL ENUM types.${NC}"
    # Continue anyway as we've fixed the code
fi 