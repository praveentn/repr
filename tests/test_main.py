# tests/test_main.py
"""
Test cases for main FastAPI application
"""

import pytest
from fastapi.testclient import TestClient

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "version" in data
    assert "components" in data

def test_home_page(client):
    """Test home page rendering."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_admin_page(client):
    """Test admin page rendering."""
    response = client.get("/admin")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_get_representations(client):
    """Test getting available representation modes."""
    response = client.get("/api/representations")
    assert response.status_code == 200
    
    data = response.json()
    assert "modes" in data
    assert isinstance(data["modes"], dict)
    assert "plain_text" in data["modes"]

def test_process_query_invalid_data(client):
    """Test processing query with invalid data."""
    response = client.post("/api/process", json={})
    assert response.status_code == 422  # Validation error

def test_upload_endpoint_no_file(client):
    """Test upload endpoint without file."""
    response = client.post("/api/upload")
    assert response.status_code == 422


