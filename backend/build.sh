#!/bin/bash

echo "Starting build process for backend deployment..."

# Install Python dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt --no-cache-dir

# Run the package optimization script
echo "Running package optimization to reduce deployment size..."
python slim_deployment.py

# Clean up unnecessary files to reduce deployment size
echo "Cleaning project directory..."

# Remove Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete

# Remove unnecessary directories and files
find . -type d -name "tests" -exec rm -rf {} +
find . -type f -name ".DS_Store" -delete
find . -type f -name ".gitignore" -delete

# Remove large development-only files
if [ -f "generate_mock_data.py" ]; then
  echo "Removing generate_mock_data.py..."
  rm generate_mock_data.py
fi

if [ -f "initialize_vector_store.py" ]; then
  echo "Removing initialize_vector_store.py..."
  rm initialize_vector_store.py
fi

if [ -f "debug_vector_store.py" ]; then
  echo "Removing debug_vector_store.py..."
  rm debug_vector_store.py
fi

# You can add more specific cleanup tasks here

echo "Build process completed successfully!" 