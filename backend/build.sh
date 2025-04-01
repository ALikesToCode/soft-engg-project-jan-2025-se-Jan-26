#!/bin/bash

echo "Running custom build script..."

# Install dependencies
echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Run the optimization script
echo "Optimizing package size..."
python slim_deployment.py

# Remove tests and other unnecessary files from the project
echo "Cleaning project directory..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name "tests" -exec rm -rf {} +
find . -type d -name "test" -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name "*.pyd" -delete
find . -name ".DS_Store" -delete
find . -name ".gitignore" -delete
find . -name ".pytest_cache" -exec rm -rf {} +

# Remove any large unneeded files 
rm -f generate_mock_data.py
rm -f initialize_vector_store.py
rm -f debug_vector_store.py

echo "Build completed successfully!" 