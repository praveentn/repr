# tests/test_database.py
"""
Test cases for database operations
"""

import pytest
from datetime import datetime
from models.schemas import ConversationLog, RepresentationMode

@pytest.mark.asyncio
async def test_database_initialization(temp_db):
    """Test database initialization."""
    # Database should be initialized through fixture
    assert await temp_db.health_check()

@pytest.mark.asyncio
async def test_save_conversation(temp_db):
    """Test saving conversation to database."""
    conversation_log = ConversationLog(
        session_id="test-session-123",
        user_query="What is AI?",
        llm_response="AI is artificial intelligence...",
        representation_mode=RepresentationMode.PLAIN_TEXT,
        token_usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        processing_time=1.5,
        llm_config={"model": "test-model"},
        timestamp=datetime.now()
    )
    
    conversation_id = await temp_db.save_conversation(conversation_log)
    assert conversation_id is not None
    assert isinstance(conversation_id, int)

@pytest.mark.asyncio
async def test_get_session(temp_db):
    """Test retrieving session data."""
    # First save a conversation
    conversation_log = ConversationLog(
        session_id="test-session-456",
        user_query="Test query",
        representation_mode=RepresentationMode.PLAIN_TEXT,
        timestamp=datetime.now()
    )
    
    await temp_db.save_conversation(conversation_log)
    
    # Then retrieve session
    session_data = await temp_db.get_session("test-session-456")
    assert session_data is not None
    assert "session" in session_data
    assert "conversations" in session_data

@pytest.mark.asyncio
async def test_get_system_stats(temp_db):
    """Test getting system statistics."""
    stats = await temp_db.get_system_stats()
    
    assert isinstance(stats, dict)
    assert "total_conversations" in stats
    assert "total_sessions" in stats
    assert isinstance(stats["total_conversations"], int)

@pytest.mark.asyncio
async def test_get_table_list(temp_db):
    """Test getting database table list."""
    tables = await temp_db.get_table_list()
    
    assert isinstance(tables, list)
    assert "conversations" in tables
    assert "user_sessions" in tables


