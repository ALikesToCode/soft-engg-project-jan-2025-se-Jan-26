#!/usr/bin/env python3
"""
Test script for the vector store.
Run this after initialize_vector_store.py to check if the vector store is working properly.
"""

import os
import logging
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set")

def test_vector_store():
    """Test querying the vector store with a few sample queries"""
    # Set up Google Embeddings
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    # Connect to the vector store
    try:
        logger.info("Connecting to vector store...")
        vector_store = PGVector(
            embeddings=embeddings,
            collection_name="vector_store",
            connection_string=database_url
        )
        logger.info("Successfully connected to vector store")
    except Exception as e:
        logger.error(f"Error connecting to vector store: {str(e)}")
        raise
    
    # Test queries
    test_queries = [
        "What are software design patterns?",
        "Explain version control systems like Git",
        "How do I conduct a code review?",
        "What is the difference between agile and waterfall methodologies?",
        "What are the key aspects of software testing?"
    ]
    
    for query in test_queries:
        logger.info(f"Testing query: '{query}'")
        try:
            # Search for documents
            docs = vector_store.similarity_search(query, k=2)
            
            # Print results
            logger.info(f"Found {len(docs)} results for '{query}'")
            for i, doc in enumerate(docs):
                logger.info(f"Result {i+1}:")
                logger.info(f"Source: {doc.metadata.get('source', 'Unknown')}")
                logger.info(f"Page: {doc.metadata.get('page', 0)}")
                logger.info(f"Content (first 150 chars): {doc.page_content[:150]}...")
                logger.info("-" * 50)
        except Exception as e:
            logger.error(f"Error querying vector store for '{query}': {str(e)}")
    
    logger.info("Vector store test completed")

if __name__ == "__main__":
    test_vector_store() 