# tests/test_representations.py
"""
Test cases for representation engine
"""

import pytest
from core.representations import RepresentationEngine

@pytest.mark.asyncio
async def test_plain_text_representation(representation_engine):
    """Test plain text representation generation."""
    content = "This is a test content for plain text representation."
    
    result = await representation_engine.generate_representation(
        content=content,
        mode="plain_text"
    )
    
    assert result.mode == "plain_text"
    assert "text" in result.content
    assert result.content["text"] == content

@pytest.mark.asyncio
async def test_color_coded_representation(representation_engine):
    """Test color-coded representation generation."""
    content = """
    This is a fact about AI. We assume that AI will continue to grow.
    For example, machine learning is widely used. Warning: AI has risks.
    """
    
    result = await representation_engine.generate_representation(
        content=content,
        mode="color_coded"
    )
    
    assert result.mode == "color_coded"
    assert "sections" in result.content
    assert "legend" in result.content
    assert isinstance(result.content["sections"], dict)

@pytest.mark.asyncio
async def test_knowledge_graph_representation(representation_engine):
    """Test knowledge graph representation generation."""
    content = "Artificial Intelligence includes Machine Learning and Deep Learning."
    
    result = await representation_engine.generate_representation(
        content=content,
        mode="knowledge_graph"
    )
    
    assert result.mode == "knowledge_graph"
    assert "graph_data" in result.content
    assert "entities" in result.content
    assert "relationships" in result.content

@pytest.mark.asyncio
async def test_invalid_representation_mode(representation_engine):
    """Test handling of invalid representation mode."""
    content = "Test content"
    
    result = await representation_engine.generate_representation(
        content=content,
        mode="invalid_mode"
    )
    
    # Should fallback to plain_text
    assert result.mode == "plain_text"

def test_get_available_modes(representation_engine):
    """Test getting available representation modes."""
    modes = representation_engine.get_available_modes()
    
    assert isinstance(modes, dict)
    assert "plain_text" in modes
    assert "color_coded" in modes
    assert "knowledge_graph" in modes
    
    # Check mode structure
    plain_text_mode = modes["plain_text"]
    assert "name" in plain_text_mode
    assert "description" in plain_text_mode
    assert "icon" in plain_text_mode


