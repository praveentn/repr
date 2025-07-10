# tests/test_integration.py
"""
Integration tests for the complete system
"""

import pytest
import json

@pytest.mark.asyncio
async def test_complete_query_processing_flow(client, mock_llm_manager):
    """Test complete query processing flow."""
    # Mock the LLM manager in the app
    import main
    main.llm_manager = mock_llm_manager
    
    query_data = {
        "query": "Explain machine learning",
        "representation_mode": "plain_text",
        "user_preferences": {"complexity_level": "beginner"}
    }
    
    response = client.post("/api/process", json=query_data)
    
    assert response.status_code == 200
    
    data = response.json()
    assert "session_id" in data
    assert "original_query" in data
    assert "llm_response" in data
    assert "representation" in data
    assert "processing_time" in data
    assert "token_usage" in data
    
    assert data["original_query"] == query_data["query"]
    assert data["mode"] == query_data["representation_mode"]

def test_admin_stats_endpoint(client):
    """Test admin statistics endpoint."""
    response = client.get("/api/admin/stats")
    
    # Should work even without authentication in test mode
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)

def test_file_upload_json(client):
    """Test JSON file upload."""
    test_data = {"test": "data", "number": 123}
    json_content = json.dumps(test_data)
    
    files = {"file": ("test.json", json_content, "application/json")}
    response = client.post("/api/upload", files=files)
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["data"] == test_data

def test_error_handling(client):
    """Test error handling for invalid requests."""
    # Test with malformed JSON
    response = client.post("/api/process", 
                          data="invalid json",
                          headers={"content-type": "application/json"})
    
    assert response.status_code == 422


