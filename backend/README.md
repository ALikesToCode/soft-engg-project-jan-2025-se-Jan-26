# Backend Setup and Running Guide

This guide provides comprehensive instructions for setting up and running the backend server.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL
- Redis (optional, for caching and session management)

## Setup Steps

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/Mac
source .venv/bin/activate
# On Windows
# .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup PostgreSQL

```bash
# Install PostgreSQL (Debian/Ubuntu)
sudo apt install postgresql

# Access PostgreSQL command line
sudo -i -u postgres
psql

# Setup database and user
postgres=# ALTER USER postgres PASSWORD 'your_password';
postgres=# CREATE DATABASE se_project_db;
postgres=# \q
```

### 4. Configure Environment Variables

Create a `.env` file in the backend directory by copying the `.env.example` file:

```bash
cp .env.example .env
```

Then update the following variables in your `.env` file:

```
# Server Configuration
PORT=8000
HOST=0.0.0.0
ENV=development

# Database Configuration 
# Format: postgres://<user>:<password>@<host>/<database>?sslmode=require
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/se_project_db

# Authentication
SESSION_SECRET=your_super_secret_key  # Generate a strong random string

# Frontend URLs (for CORS)
FRONTEND_URL=http://localhost:5173
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000

# API Configuration
API_PREFIX=/api/v1

# Application
APP_NAME="SE Team 26 API"
APP_DESCRIPTION="Backend API for SE Team 26 Project"
APP_VERSION="1.0.0"

# Redis (if using Redis)
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API Health Check
API_HEALTH_URL=http://localhost:8000/health

# Monitoring
MONITORING_METRICS_HISTORY_SIZE=1000
MONITORING_HEALTH_CHECK_INTERVAL=60

# Logflare Settings
USE_LOGFLARE=true
LOGFLARE_SOURCE_ID=your_logflare_source_id
LOGFLARE_API_KEY=your_logflare_api_key
LOGFLARE_BATCH_SIZE=10
LOGFLARE_LOG_LEVEL=INFO

# Alert Thresholds (adjust based on your requirements)
ALERT_THRESHOLD_CPU=80.0        # CPU usage percentage threshold
ALERT_THRESHOLD_MEMORY=85.0     # Memory usage percentage threshold
ALERT_THRESHOLD_DISK=90.0       # Disk usage percentage threshold
ALERT_THRESHOLD_RESPONSE_TIME=2000.0  # Response time in milliseconds
ALERT_THRESHOLD_ERROR_RATE=5.0  # Error rate percentage threshold

# LLM Configuration (if using LLM features)
LANGSMITH_TRACING=your_langsmith_tracing
LANGSMITH_ENDPOINT=your_langsmith_endpoint
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=your_langsmith_project
GOOGLE_API_KEY=your_google_api_key

# JWT Configuration
JWT_SECRET=your_jwt_secret_key  # Generate a strong random string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 5. Database Migrations

If migrations are needed, run:

```bash
python migrate.py
```

### 6. Start the Backend Server

#### Development mode:

```bash
# Start with auto-reload enabled
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Production mode:

```bash
# Start without auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000
```

Alternatively, you can use the provided shell script:

```bash
# Make sure the script is executable
chmod +x run.sh

# Run the server
./run.sh
```

## API Documentation

Once the server is running, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Running Tests

```bash
# Run all tests
pytest

# Or use the shell script
chmod +x run_tests.sh
./run_tests.sh
```

## Monitoring

The application logs are sent to Logflare for centralized logging. You can view the logs in the Logflare dashboard at:

```
https://logflare.app/sources/YOUR_SOURCE_ID
```

When Logflare is disabled, logs are stored in the `logs` directory.
