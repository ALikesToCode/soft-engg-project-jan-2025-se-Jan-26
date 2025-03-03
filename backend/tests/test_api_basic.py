import pytest
import requests
import json
import uuid
from datetime import datetime, timedelta

def test_api_root():
    """Test that the API root endpoint is accessible"""
    response = requests.get("http://localhost:8000/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Welcome to SE Team 26 API" in data["message"]

def test_api_docs():
    """Test that the API docs endpoint is accessible"""
    response = requests.get("http://localhost:8000/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text 