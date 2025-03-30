#!/bin/bash
# Install required packages for data generation and checking

echo "Installing required packages for data generation scripts..."

# Check if venv is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Virtual environment not activated. Attempting to activate..."
    
    # Check if .venv directory exists
    if [ -d ".venv" ]; then
        source .venv/bin/activate
        echo "Activated virtual environment from .venv"
    elif [ -d "venv" ]; then
        source venv/bin/activate
        echo "Activated virtual environment from venv"
    else
        echo "No virtual environment found. Creating one..."
        python -m venv .venv
        source .venv/bin/activate
        echo "Created and activated virtual environment"
    fi
else
    echo "Virtual environment already activated: $VIRTUAL_ENV"
fi

# Install required packages
echo "Installing packages..."
pip install faker psycopg tabulate python-dotenv bcrypt

echo "Making scripts executable..."
chmod +x generate_mock_data.py
chmod +x check_all_tables.py

echo "Installation complete. You can now run the data scripts:"
echo "  - ./check_all_tables.py                # Check all tables"
echo "  - ./check_all_tables.py [table_name]   # Describe a specific table"
echo "  - ./generate_mock_data.py              # Generate mock data" 