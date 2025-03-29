# SE Team 26 Backend API

This is the backend API for the SE Team 26 Project.

## Features

- User authentication (JWT-based)
- Google OAuth integration
- Course management
- Assignment management
- File uploads with S3 storage support
- Plagiarism detection
- Grading system
- Monitoring and health checks

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- Redis (optional)
- S3-compatible storage (for production)

### Installation

1. Clone the repository
2. Navigate to the backend directory
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following variables:

```
# Database and Authentication
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
SESSION_SECRET=your_session_secret
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
FRONTEND_URL=http://localhost:5173
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# S3 Storage (optional for local development)
S3_ACCESS_KEY=your_s3_access_key
S3_SECRET_KEY=your_s3_secret_key
S3_ENDPOINT_URL=your_s3_endpoint_url
S3_BUCKET_NAME=your_s3_bucket_name
S3_REGION=auto
```

5. Run the application:

```bash
uvicorn main:app --reload
```

## File Storage

The application supports two modes of file storage:

1. **Local filesystem** (default for development)
   - Files are stored in the `uploads` directory
   - No additional configuration required

2. **S3-compatible storage** (required for production/Vercel)
   - Files are stored in an S3-compatible storage service (like Cloudflare R2)
   - Configure using the S3 environment variables
   - Automatically used when running in a read-only environment (like Vercel)

## Deployment

### Local Deployment

For local deployment, follow the installation steps above.

### Vercel Deployment

For deploying to Vercel, see [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md) for detailed instructions.

Key points for Vercel deployment:
- Vercel has a read-only filesystem, so file uploads use S3-compatible storage
- Redis connection is optional with an in-memory fallback
- Environment variables need to be configured in the Vercel dashboard

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run tests with pytest:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Vector Store Retrieval

This application includes a vector store for retrieving relevant information from course materials. The vector store is implemented using:

- PostgreSQL with pgvector extension for storing embeddings
- Google's text-embedding-004 model for generating embeddings
- LangChain's PGVector implementation for integrating with the database

### Setup

The vector store is automatically initialized when the application starts for the first time. The initialization process:

1. Loads PDF files from the `pdfs` directory
2. Splits them into smaller chunks
3. Generates embeddings for each chunk
4. Stores the embeddings and document content in the PostgreSQL database

### Usage

The vector store is used by the chat functionality to retrieve relevant information from course materials when users ask questions. The LLM will call the `query_course_materials` function when appropriate to get information from the stored documents.

### Manual Initialization

If you need to manually reinitialize the vector store, you can:

1. Delete the `vector_store_initialized.flag` file in the backend directory
2. Restart the server, or run `python initialize_vector_store.py` directly

For more detailed information, see the [VECTOR_STORE_SETUP.md](VECTOR_STORE_SETUP.md) file.
