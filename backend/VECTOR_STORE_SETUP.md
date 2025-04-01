# Vector Store Setup and Troubleshooting Guide

This document provides detailed information about setting up and troubleshooting the vector store functionality used for document retrieval in the application.

## Overview

The application uses a vector store based on PostgreSQL with the pgvector extension to provide semantic search capabilities for course materials. Documents are loaded, split into chunks, embedded using Google's text-embedding-004 model, and stored in a PostgreSQL database for efficient retrieval.

## Requirements

- PostgreSQL database with pgvector extension installed
- Google Generative AI API key for embeddings generation
- Course materials in PDF format (stored in the `pdfs` directory)

## Setup Process

### 1. Database Configuration

The application uses your PostgreSQL database (configured in `.env`) with the pgvector extension. The database user must have permission to create extensions if pgvector is not already installed.

```sql
-- This command must be run as a superuser
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2. Environment Variables

Ensure these environment variables are set in your `.env` file:

```
DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname?sslmode=require
GOOGLE_API_KEY=your-google-api-key
```

### 3. PDF Documents

Place your PDF documents in the `pdfs` directory in the backend folder. These will be processed and indexed automatically.

### 4. Initializing the Vector Store

The vector store is automatically initialized when the application starts for the first time. The initialization process:

1. Loads PDF documents from the `pdfs` directory
2. Splits documents into smaller chunks
3. Generates embeddings for each chunk using Google's text-embedding-004 model
4. Stores the chunks and embeddings in the PostgreSQL database

A flag file (`vector_store_initialized.flag`) is created after successful initialization to prevent reprocessing on subsequent startups.

## Troubleshooting

If you encounter issues with the vector store initialization, follow these steps:

### 1. Run the Diagnostics Script

```bash
python debug_vector_store.py
```

This script will:
- Check your environment variables
- Test the database connection and pgvector extension
- Verify LangChain package versions
- Test embeddings generation
- Attempt to create a test vector store
- Provide detailed diagnostic information

### 2. Common Issues and Solutions

#### pgvector Extension Not Available

If you see an error like `extension "vector" is not available`, the pgvector extension may not be installed on your PostgreSQL server.

**Solution**: Install the pgvector extension on your PostgreSQL server:

```sql
CREATE EXTENSION vector;
```

Note: This requires superuser privileges on the database server.

#### Package Compatibility Issues

If you encounter API compatibility issues between different LangChain packages, run:

```bash
pip install langchain-postgres==0.0.1 pgvector==0.2.5
```

#### API Parameter Errors

The LangChain PostgreSQL vector store API may have changed between versions. The diagnostics script tries different parameter combinations to find what works with your installed version.

### 3. Manual Reinitialization

To force reinitialization of the vector store:

1. Delete the flag file:
   ```bash
   rm vector_store_initialized.flag
   ```

2. Restart the application:
   ```bash
   python -m uvicorn main:app --reload
   ```

Or run the debug script which will reset the flags for you:
```bash
python debug_vector_store.py
```

### 4. Version Information

Current tested versions:
- langchain-postgres: 0.0.1
- pgvector: 0.2.5
- langchain-community: 0.0.24
- PyMuPDF: 1.22.0+

## Manually Adding Documents

To manually add new documents to the vector store after initialization:

1. Add your PDF files to the `pdfs` directory
2. Delete the `vector_store_initialized.flag` file
3. Restart the application

The vector store will be reinitialized with all documents in the directory.

## Database Connection String Format

The connection string format should be:

```
postgresql://username:password@hostname:port/database?sslmode=require
```

Note: When using with SQLAlchemy, the format is:

```
postgresql+asyncpg://username:password@hostname:port/database?sslmode=require
```

But for direct PGVector initialization, the format should be:

```
postgresql://username:password@hostname:port/database?sslmode=require
```

The application automatically converts between these formats as needed. 