# tests/conftest.py
"""
Test configuration and fixtures for Knowledge Representation Engine
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from typing import AsyncGenerator, Generator
import aiosqlite
from fastapi.testclient import TestClient

# Add project root to path
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import app
from core.database import DatabaseManager
from core.llm_manager import LLMManager
from core.representations import RepresentationEngine
from config.settings import Settings

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
async def temp_db():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_knowledge_repr.db"
    
    # Initialize test database
    db_manager = DatabaseManager(str(db_path))
    await db_manager.initialize()
    
    yield db_manager
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()
    os.rmdir(temp_dir)

@pytest.fixture
def mock_llm_manager():
    """Create a mock LLM manager for testing."""
    class MockLLMManager:
        def __init__(self):
            self.config = {
                "model": "test-model",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        
        async def initialize(self):
            pass
        
        async def generate_response(self, query, context=None, representation_mode="plain_text"):
            from core.llm_manager import LLMResponse
            return LLMResponse(
                content=f"Mock response for: {query}",
                usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
                model="test-model",
                response_time=0.1,
                timestamp="2024-01-01T00:00:00"
            )
        
        def get_current_config(self):
            return self.config
        
        async def health_check(self):
            return True
    
    return MockLLMManager()

@pytest.fixture
def representation_engine():
    """Create a representation engine for testing."""
    return RepresentationEngine()

@pytest.fixture
def sample_query_request():
    """Sample query request for testing."""
    return {
        "query": "Explain artificial intelligence",
        "context": {"user_level": "beginner"},
        "representation_mode": "plain_text",
        "user_preferences": {"style": "modern"}
    }

@pytest.fixture
def sample_knowledge_graph_data():
    """Sample knowledge graph data for testing."""
    return {
        "nodes": [
            {"id": "ai", "label": "Artificial Intelligence", "type": "concept"},
            {"id": "ml", "label": "Machine Learning", "type": "subconcept"},
            {"id": "dl", "label": "Deep Learning", "type": "subconcept"}
        ],
        "edges": [
            {"from": "ai", "to": "ml", "label": "includes"},
            {"from": "ml", "to": "dl", "label": "includes"}
        ]
    }

@pytest.fixture
def sample_timeline_events():
    """Sample timeline events for testing."""
    return [
        {"date": "1950", "event": "Turing Test proposed", "importance": 5},
        {"date": "1956", "event": "Dartmouth Conference", "importance": 5},
        {"date": "1997", "event": "Deep Blue beats Kasparov", "importance": 4}
    ]

# Test configuration
pytest_plugins = ["pytest_asyncio"]

# Configure test settings
class TestSettings(Settings):
    """Test-specific settings."""
    def __init__(self):
        super().__init__()
        self.app.debug = True
        self.database.db_path = ":memory:"
        self.azure_openai.api_key = "test-key"
        self.azure_openai.endpoint = "https://test.openai.azure.com/"

# Override settings for testing
import config.settings
config.settings.config = TestSettings()


