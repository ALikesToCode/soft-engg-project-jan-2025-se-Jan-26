"""
Debug and fix Vector Store initialization

This script helps diagnose issues with the vector store setup
and provides helpful information for fixing them.
"""
import os
import sys
import logging
import inspect
import pkg_resources
from dotenv import load_dotenv
import importlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def check_environment():
    """Check environment variables and configurations"""
    # Check DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL environment variable is not set")
        return False
    logger.info(f"Using DATABASE_URL: {database_url}")
    
    # Check Google API key
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        logger.error("GOOGLE_API_KEY environment variable is not set")
        return False
    logger.info("GOOGLE_API_KEY is set")
    
    # Convert SQLAlchemy URL format to psycopg format
    psycopg_connection_string = database_url
    if "postgresql+asyncpg://" in psycopg_connection_string:
        psycopg_connection_string = psycopg_connection_string.replace("postgresql+asyncpg://", "postgresql://")
        logger.info(f"Converted connection string for psycopg: {psycopg_connection_string}")
    
    return psycopg_connection_string

def check_database_connection(connection_string):
    """Check connection to PostgreSQL database"""
    try:
        import psycopg
        logger.info("Connecting to PostgreSQL...")
        
        with psycopg.connect(connection_string) as conn:
            with conn.cursor() as cur:
                # Get PostgreSQL version
                cur.execute("SELECT version()")
                version = cur.fetchone()
                logger.info(f"PostgreSQL Version: {version[0]}")
                
                # Check for pgvector extension
                cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'")
                pgvector = cur.fetchone()
                if pgvector:
                    logger.info(f"pgvector extension is installed (version: {pgvector[1]})")
                else:
                    logger.warning("pgvector extension is NOT installed")
                    
                    # Try to install it
                    try:
                        logger.info("Attempting to install pgvector extension...")
                        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                        conn.commit()
                        logger.info("pgvector extension installed successfully")
                    except Exception as e:
                        logger.error(f"Failed to install pgvector extension: {e}")
                        return False
                        
                # Test if we can create a vector column (if pgvector is installed)
                try:
                    cur.execute("CREATE TEMP TABLE vector_test (id SERIAL PRIMARY KEY, embedding VECTOR(3))")
                    cur.execute("INSERT INTO vector_test (embedding) VALUES ('[1, 2, 3]')")
                    cur.execute("SELECT * FROM vector_test")
                    result = cur.fetchone()
                    logger.info(f"Vector test successful: {result}")
                except Exception as e:
                    logger.error(f"Vector test failed: {e}")
                    return False
        
        logger.info("Database connection test completed successfully")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def check_langchain_packages():
    """Check langchain packages and versions"""
    packages = [
        "langchain",
        "langchain-postgres",
        "langchain-community",
        "pgvector",
        "PyMuPDF"
    ]
    
    for package in packages:
        try:
            version = pkg_resources.get_distribution(package).version
            logger.info(f"{package} version: {version}")
        except Exception:
            logger.error(f"{package} is not installed")
            return False
    
    # Check if langchain-postgres can be imported
    try:
        from langchain_postgres import PGVector
        logger.info("Successfully imported PGVector from langchain_postgres")
        
        # Inspect PGVector class
        logger.info("PGVector class methods:")
        methods = [method for method in dir(PGVector) if not method.startswith('_')]
        logger.info(f"Available methods: {methods}")
        
        # Inspect constructor parameters
        params = inspect.signature(PGVector.__init__).parameters
        logger.info(f"PGVector constructor parameters: {list(params.keys())}")
        
        # Check if from_connection_string is available
        if hasattr(PGVector, 'from_connection_string'):
            logger.info("PGVector has from_connection_string class method")
        else:
            logger.warning("PGVector doesn't have from_connection_string method")
            if hasattr(PGVector, 'get_connection_string'):
                logger.info("PGVector has get_connection_string method instead")
    except Exception as e:
        logger.error(f"Error importing langchain_postgres: {e}")
        return False
    
    return True

def test_embeddings():
    """Test embeddings generation"""
    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        
        # Check if Google API key is set
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            logger.error("GOOGLE_API_KEY environment variable is not set")
            return False
        
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=google_api_key
        )
        
        # Test embedding generation
        test_text = "This is a test sentence for embeddings."
        result = embeddings.embed_query(test_text)
        
        logger.info(f"Successfully generated embeddings with {len(result)} dimensions")
        return True
    except Exception as e:
        logger.error(f"Error testing embeddings: {e}")
        return False

def fix_package_versions():
    """Fix package versions to ensure compatibility"""
    logger.info("Installing compatible package versions...")
    
    try:
        import subprocess
        # Install specific version of langchain-postgres
        result = subprocess.run(
            ["pip", "install", "--upgrade", "langchain-postgres==0.0.1"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info("Successfully installed langchain-postgres==0.0.1")
        else:
            logger.error(f"Failed to install langchain-postgres: {result.stderr}")
            
        # Install pgvector
        result = subprocess.run(
            ["pip", "install", "--upgrade", "pgvector==0.2.5"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info("Successfully installed pgvector==0.2.5")
        else:
            logger.error(f"Failed to install pgvector: {result.stderr}")
            
        # Reload modules
        if 'langchain_postgres' in sys.modules:
            importlib.reload(sys.modules['langchain_postgres'])
        if 'pgvector' in sys.modules:
            importlib.reload(sys.modules['pgvector'])
            
        logger.info("Package versions fixed")
        return True
    except Exception as e:
        logger.error(f"Error fixing package versions: {e}")
        return False

def create_vector_store(connection_string):
    """Try to create a vector store"""
    try:
        from langchain_postgres import PGVector
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        
        # Check if Google API key is set
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            logger.error("GOOGLE_API_KEY environment variable is not set")
            return False
        
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=google_api_key
        )
        
        # Inspect PGVector constructor
        params = inspect.signature(PGVector.__init__).parameters
        logger.info(f"PGVector constructor parameters: {list(params.keys())}")
        
        # Try different parameter combinations
        try:
            logger.info("Trying with 'embedding' parameter")
            vector_store = PGVector(
                embedding=embeddings,
                collection_name="vector_store_test",
                connection_string=connection_string
            )
            logger.info("Successfully created vector store with 'embedding' parameter")
            return True
        except Exception as e:
            logger.warning(f"Failed with 'embedding' parameter: {e}")
            
            try:
                logger.info("Trying with 'embeddings' parameter")
                vector_store = PGVector(
                    embeddings=embeddings,
                    collection_name="vector_store_test",
                    connection_string=connection_string
                )
                logger.info("Successfully created vector store with 'embeddings' parameter")
                return True
            except Exception as e:
                logger.warning(f"Failed with 'embeddings' parameter: {e}")
                
                try:
                    logger.info("Trying with 'embedding_function' parameter")
                    vector_store = PGVector(
                        embedding_function=embeddings,
                        collection_name="vector_store_test",
                        connection_string=connection_string
                    )
                    logger.info("Successfully created vector store with 'embedding_function' parameter")
                    return True
                except Exception as e:
                    logger.error(f"Failed with all parameter combinations: {e}")
                    return False
    except Exception as e:
        logger.error(f"Error creating vector store: {e}")
        return False

def reset_vector_store():
    """Reset vector store by deleting flag file"""
    try:
        flag_file = "vector_store_initialized.flag"
        if os.path.exists(flag_file):
            os.remove(flag_file)
            logger.info(f"Deleted {flag_file}")
        
        unavailable_flag = "vector_store_unavailable.flag"
        if os.path.exists(unavailable_flag):
            os.remove(unavailable_flag)
            logger.info(f"Deleted {unavailable_flag}")
            
        logger.info("Vector store flags reset. The server will try to initialize the vector store on next startup.")
        return True
    except Exception as e:
        logger.error(f"Error resetting vector store: {e}")
        return False

def main():
    """Main function to run diagnostics and fixes"""
    logger.info("=== Vector Store Diagnostics ===")
    
    # Check environment
    logger.info("\n=== Checking Environment ===")
    connection_string = check_environment()
    if not connection_string:
        logger.error("Environment check failed")
        return
    
    # Check database connection
    logger.info("\n=== Checking Database Connection ===")
    if not check_database_connection(connection_string):
        logger.error("Database connection check failed")
        return
    
    # Check langchain packages
    logger.info("\n=== Checking LangChain Packages ===")
    if not check_langchain_packages():
        logger.warning("LangChain packages check failed")
        
        # Try to fix package versions
        logger.info("\n=== Fixing Package Versions ===")
        if not fix_package_versions():
            logger.error("Failed to fix package versions")
            return
        
        # Check packages again
        logger.info("\n=== Checking LangChain Packages Again ===")
        if not check_langchain_packages():
            logger.error("LangChain packages check failed again")
            return
    
    # Test embeddings
    logger.info("\n=== Testing Embeddings ===")
    if not test_embeddings():
        logger.error("Embeddings test failed")
        return
    
    # Try to create vector store
    logger.info("\n=== Testing Vector Store Creation ===")
    if not create_vector_store(connection_string):
        logger.error("Vector store creation failed")
        return
    
    # Reset vector store
    logger.info("\n=== Resetting Vector Store ===")
    if not reset_vector_store():
        logger.error("Vector store reset failed")
        return
    
    logger.info("\n=== All Tests Passed ===")
    logger.info("You can now restart the server to initialize the vector store.")

if __name__ == "__main__":
    main() 