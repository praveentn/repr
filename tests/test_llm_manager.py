# tests/test_llm_manager.py
"""
Test cases for LLM manager (using mock)
"""

import pytest

@pytest.mark.asyncio
async def test_llm_manager_initialization(mock_llm_manager):
    """Test LLM manager initialization."""
    await mock_llm_manager.initialize()
    # Should not raise any exceptions

@pytest.mark.asyncio
async def test_generate_response(mock_llm_manager):
    """Test generating response from LLM."""
    query = "What is artificial intelligence?"
    
    response = await mock_llm_manager.generate_response(query)
    
    assert response.content.startswith("Mock response for:")
    assert query in response.content
    assert response.usage["total_tokens"] == 30
    assert response.model == "test-model"

@pytest.mark.asyncio
async def test_generate_response_with_context(mock_llm_manager):
    """Test generating response with context."""
    query = "Continue the explanation"
    context = {"previous": "We were talking about AI"}
    
    response = await mock_llm_manager.generate_response(query, context)
    
    assert response.content is not None
    assert isinstance(response.usage, dict)

def test_get_current_config(mock_llm_manager):
    """Test getting current LLM configuration."""
    config = mock_llm_manager.get_current_config()
    
    assert isinstance(config, dict)
    assert "model" in config
    assert "temperature" in config
    assert "max_tokens" in config

@pytest.mark.asyncio
async def test_health_check(mock_llm_manager):
    """Test LLM health check."""
    health = await mock_llm_manager.health_check()
    assert health is True


