#!/bin/bash
clear
echo "==========================#############==============================="
echo "I will do the server set up and initiate it for you."
echo "You can re-run me without any issues."
echo "==========================#############==============================="

if [ -d ".venv" ]; then
    echo "Virtual environment exists. Enabling the virtual env"
    source .venv/bin/activate
else
    echo "No Virtual environment found."
    echo "Creating venv and installing dependencies..."

    python3 -m venv .venv
    source .venv/bin/activate
    
    echo "Virtual environment activated."
    python3 -m pip install --upgrade pip

    if [ -f "requirements.txt" ]; then
        echo "Installing dependencies from requirements.txt..."
        pip install -r requirements-full.txt
    else
        echo "requirements.txt not found! Skipping dependency installation."
    fi
    echo "==========================#############==============================="
fi

if ! pip list | grep -i "uvicorn" > /dev/null; then
    echo "Uvicorn not found. Installing..."
    pip install uvicorn
fi

echo "Starting the server..."
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
