from langchain_community.document_loaders import PyMuPDFLoader
import os
import logging
from dotenv import load_dotenv
import inspect

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set")

# Verify the connection string is properly formatted
if not database_url.endswith("require"):
    logger.warning(f"Invalid DATABASE_URL format: {database_url}")
    if "?sslmode" in database_url:
        # Fix common issue with sslmode parameter
        database_url = database_url.replace("?sslmode", "?sslmode=require")
        logger.info(f"Fixed DATABASE_URL: {database_url}")
    else:
        logger.warning("Could not auto-fix DATABASE_URL")

# PGVector requires the regular PostgreSQL URL format without the dialect prefix
pgvector_connection_string = database_url
if "postgresql+asyncpg://" in pgvector_connection_string:
    pgvector_connection_string = pgvector_connection_string.replace("postgresql+asyncpg://", "postgresql://")
    logger.info(f"Converted connection string format for PGVector: {pgvector_connection_string}")

# Ensure pgvector extension is installed
try:
    import psycopg
    logger.info(f"Connecting to PostgreSQL using: {pgvector_connection_string[:pgvector_connection_string.index('@')]}")
    with psycopg.connect(pgvector_connection_string) as conn:
        with conn.cursor() as cur:
            # First check if we can query the database at all
            logger.info("Testing database connection...")
            cur.execute("SELECT version()")
            version = cur.fetchone()
            logger.info(f"Connected to PostgreSQL: {version[0] if version else 'Unknown'}")
            
            # Check if we have permission to create extensions
            try:
                cur.execute("SELECT usesuper FROM pg_user WHERE usename = current_user")
                is_superuser = cur.fetchone()
                logger.info(f"Current user is superuser: {bool(is_superuser[0]) if is_superuser else 'Unknown'}")
            except Exception as e:
                logger.warning(f"Could not check superuser status: {e}")
            
            # Check if pgvector extension is installed
            cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            if not cur.fetchone():
                logger.info("Vector extension not found, attempting to install pgvector extension...")
                try:
                    cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                    conn.commit()
                    logger.info("pgvector extension installed successfully")
                except Exception as e:
                    logger.error(f"Failed to install pgvector extension: {e}")
                    logger.error("Your database may not have pgvector installed at the system level")
                    logger.error("Contact your database administrator or see: https://github.com/pgvector/pgvector")
                    raise Exception(f"pgvector extension could not be installed: {e}")
            else:
                logger.info("pgvector extension is already installed")
except Exception as e:
    logger.error(f"Database connection or pgvector verification failed: {e}")
    logger.error("Make sure your PostgreSQL server is running and has pgvector installed")
    raise

def load_pdfs(pdf_paths):
    documents = []
    for path in pdf_paths:
        logger.info(f"Loading PDF: {path}")
        loader = PyMuPDFLoader(path)
        docs = loader.load()
        documents.extend(docs)
    return documents

# Find all PDF files in the pdfs directory
pdf_paths = []
pdf_dir = os.path.join("pdfs")
if not os.path.exists(pdf_dir):
    raise ValueError(f"PDF directory {pdf_dir} does not exist")

for file in os.listdir(pdf_dir):
    if file.endswith(".pdf"):
        pdf_paths.append(os.path.join(pdf_dir, file))

logger.info(f"PDF files found: {len(pdf_paths)}")

documents = load_pdfs(pdf_paths)
logger.info(f"Number of documents loaded: {len(documents)}")

from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_documents(documents, chunk_size=1000, chunk_overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    split_docs = []
    for doc in documents:
        splits = text_splitter.split_documents([doc])
        split_docs.extend(splits)
    return split_docs

split_docs = split_documents(documents)
logger.info(f"Number of chunks: {len(split_docs)}")

# Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Check if Google API key is set
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=google_api_key
)

# Initialize the vector store with pgvector
from langchain_postgres import PGVector

# Create the vector store
try:
    logger.info("Initializing vector store...")
    
    # Get detailed parameter information for better debugging
    pgvector_params = inspect.signature(PGVector.__init__).parameters
    param_details = {name: str(param.annotation) for name, param in pgvector_params.items()}
    logger.info(f"Available PGVector parameters with types: {param_details}")
    
    # Now we know the correct parameter is 'connection'
    logger.info("Using 'connection' parameter with connection string")
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name="vector_store",
        connection=pgvector_connection_string
    )
    
    logger.info("Vector store initialized successfully")
except Exception as e:
    logger.error(f"Error initializing vector store: {str(e)}")
    # Get more information about langchain-postgres
    try:
        import importlib.metadata
        langchain_postgres_version = importlib.metadata.version("langchain-postgres")
        logger.error(f"langchain-postgres version: {langchain_postgres_version}")
    except Exception as ex:
        logger.error(f"Could not get additional info: {str(ex)}")
    raise

# Add documents to the vector store
from langchain_core.documents import Document
logger.info("Adding documents to vector store...")

# Process in smaller batches to avoid memory issues
batch_size = 10
total_batches = len(split_docs) // batch_size + (1 if len(split_docs) % batch_size > 0 else 0)

for i in range(0, len(split_docs), batch_size):
    batch = split_docs[i:i+batch_size]
    batch_num = i // batch_size + 1
    logger.info(f"Processing batch {batch_num}/{total_batches} - Documents {i+1} to {min(i+batch_size, len(split_docs))}")
    
    try:
        # Add the batch to the vector store
        vector_store.add_documents(batch)
        logger.info(f"Batch {batch_num}/{total_batches} added successfully")
    except Exception as e:
        logger.error(f"Error adding batch {batch_num}: {str(e)}")
        # Continue with next batch

logger.info("Vector store initialization complete!")